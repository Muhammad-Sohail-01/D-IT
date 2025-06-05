import json
import pytz
import re

from pytz.exceptions import UnknownTimeZoneError

from babel.dates import format_datetime, format_date, format_time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from urllib.parse import unquote_plus
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_encode

from odoo import Command, exceptions, http, fields, _
from odoo.http import request, route
from odoo.osv import expression
from odoo.tools import plaintext2html, DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.tools.mail import is_html_empty
from odoo.tools.misc import babel_locale_parse, get_lang
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.addons.appointment.controllers.appointment import AppointmentController


class VehicleAppointmentController(AppointmentController):
    @http.route('/get_model', type='json', auth="public")
    def get_state(self, brand_id):
        ids = {}
        if brand_id:
            models = request.env['fleet.vehicle.model'].sudo().search([('brand_id', '=', int(brand_id))])
            for data in models:
                ids[data.id] = data.name
        return ids

    @http.route(['/appointment/<int:appointment_type_id>/info'],
                type='http', auth="public", website=True, sitemap=False)
    def appointment_type_id_form(self, appointment_type_id, date_time, duration, staff_user_id=None,
                                 resource_selected_id=None, available_resource_ids=None, asked_capacity=1, **kwargs):
        """
        Render the form to get information about the user for the appointment

        :param appointment_type_id: the appointment type id related
        :param date_time: the slot datetime selected for the appointment
        :param duration: the duration of the slot
        :param staff_user_id: the user selected for the appointment
        :param resource_selected_id: the resource selected for the appointment
        :param available_resource_ids: the resources info we want to propagate that are linked to the slot time
        :param asked_capacity: the asked capacity for the appointment
        :param filter_appointment_type_ids: see ``Appointment.appointments()`` route
        """
        domain = self._appointments_base_domain(
            filter_appointment_type_ids=kwargs.get('filter_appointment_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )
        available_appointments = self._fetch_and_check_private_appointment_types(
            kwargs.get('filter_appointment_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        appointment_type = available_appointments.filtered(lambda appt: appt.id == int(appointment_type_id))

        if not appointment_type:
            raise NotFound()

        if not self._check_appointment_is_valid_slot(appointment_type, staff_user_id, resource_selected_id,
                                                     available_resource_ids, date_time, duration, asked_capacity,
                                                     **kwargs):
            raise NotFound()

        partner = self._get_customer_partner()
        partner_data = partner.read(fields=['name', 'phone', 'email'])[0] if partner else {}
        date_time = unquote_plus(date_time)
        date_time_object = datetime.strptime(date_time, dtf)
        day_name = format_datetime(date_time_object, 'EEE', locale=get_lang(request.env).code)
        date_formated = format_date(date_time_object.date(), locale=get_lang(request.env).code)
        time_locale = format_time(date_time_object.time(), locale=get_lang(request.env).code, format='short')
        resource = request.env['appointment.resource'].sudo().browse(
            int(resource_selected_id)) if resource_selected_id else request.env['appointment.resource']
        staff_user = request.env['res.users'].browse(int(staff_user_id)) if staff_user_id else request.env['res.users']
        users_possible = self._get_possible_staff_users(
            appointment_type,
            json.loads(unquote_plus(kwargs.get('filter_staff_user_ids') or '[]')),
        )
        resources_possible = self._get_possible_resources(
            appointment_type,
            json.loads(unquote_plus(kwargs.get('filter_resource_ids') or '[]')),
        )
        return request.render("appointment.appointment_form", {
            'partner_data': partner_data,
            'appointment_type': appointment_type,
            'available_appointments': available_appointments,
            'main_object': appointment_type,
            'datetime': date_time,
            'date_locale': f'{day_name} {date_formated}',
            'time_locale': time_locale,
            'datetime_str': date_time,
            'duration_str': duration,
            'duration': float(duration),
            'staff_user': staff_user,
            'resource': resource,
            'asked_capacity': int(asked_capacity),
            'timezone': request.session.get('timezone') or appointment_type.appointment_tz,  # bw compatibility
            'users_possible': users_possible,
            'resources_possible': resources_possible,
            'available_resource_ids': available_resource_ids,
            'vehicle_brands': request.env['fleet.vehicle.model.brand'].sudo().search([]),
        })

    @http.route(['/appointment/<int:appointment_type_id>/submit'],
                type='http', auth="public", website=True, methods=["POST"])
    def appointment_form_submit(self, appointment_type_id, datetime_str, duration_str, name, phone, email,
                                staff_user_id=None, available_resource_ids=None, asked_capacity=1,
                                guest_emails_str=None, **kwargs):
        """
        Create the event for the appointment and redirect on the validation page with a summary of the appointment.

        :param appointment_type_id: the appointment type id related
        :param datetime_str: the string representing the datetime
        :param duration_str: the string representing the duration
        :param name: the name of the user sets in the form
        :param phone: the phone of the user sets in the form
        :param email: the email of the user sets in the form
        :param staff_user_id: the user selected for the appointment
        :param available_resource_ids: the resources ids available for the appointment
        :param asked_capacity: asked capacity for the appointment
        :param str guest_emails: optional line-separated guest emails. It will
          fetch or create partners to add them as event attendees;
        """
        domain = self._appointments_base_domain(
            filter_appointment_type_ids=kwargs.get('filter_appointment_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )

        available_appointments = self._fetch_and_check_private_appointment_types(
            kwargs.get('filter_appointment_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        appointment_type = available_appointments.filtered(lambda appt: appt.id == int(appointment_type_id))

        if not appointment_type:
            raise NotFound()
        timezone = request.session.get('timezone') or appointment_type.appointment_tz
        tz_session = pytz.timezone(timezone)
        datetime_str = unquote_plus(datetime_str)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc).replace(
            tzinfo=None)
        duration = float(duration_str)
        date_end = date_start + relativedelta(hours=duration)
        invite_token = kwargs.get('invite_token')

        staff_user = request.env['res.users']
        resources = request.env['appointment.resource']
        resource_ids = None
        asked_capacity = int(asked_capacity)
        resources_remaining_capacity = None
        if appointment_type.schedule_based_on == 'resources':
            resource_ids = json.loads(unquote_plus(available_resource_ids))
            # Check if there is still enough capacity (in case someone else booked with a resource in the meantime)
            resources = request.env['appointment.resource'].sudo().browse(resource_ids).exists()
            if any(resource not in appointment_type.resource_ids for resource in resources):
                raise NotFound()
            resources_remaining_capacity = appointment_type._get_resources_remaining_capacity(resources, date_start,
                                                                                              date_end,
                                                                                              with_linked_resources=False)
            if resources_remaining_capacity['total_remaining_capacity'] < asked_capacity:
                return request.redirect(
                    '/appointment/%s?%s' % (appointment_type.id, keep_query('*', state='failed-resource')))
        else:
            # check availability of the selected user again (in case someone else booked while the client was entering the form)
            staff_user = request.env['res.users'].sudo().search([('id', '=', int(staff_user_id))])
            if staff_user not in appointment_type.staff_user_ids:
                raise NotFound()
            if staff_user and not staff_user.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect(
                    '/appointment/%s?%s' % (appointment_type.id, keep_query('*', state='failed-staff-user')))

        guests = None
        if appointment_type.allow_guests:
            if guest_emails_str:
                guests = request.env['calendar.event'].sudo()._find_or_create_partners(guest_emails_str)

        customer = self._get_customer_partner() or request.env['res.partner'].sudo().search([('email', '=like', email)],
                                                                                            limit=1)
        if customer:
            if not customer.mobile:
                customer.write({'mobile': phone})
            if not customer.email:
                customer.write({'email': email})
        else:
            customer = customer.create({
                'name': name,
                'phone': customer._phone_format(number=phone, country=self._get_customer_country()) or phone,
                'email': email,
                'lang': request.lang.code,
            })

        # partner_inputs dictionary structures all answer inputs received on the appointment submission: key is question id, value
        # is answer id (as string) for choice questions, text input for text questions, array of ids for multiple choice questions.
        partner_inputs = {}
        appointment_question_ids = appointment_type.question_ids.ids
        for k_key, k_value in [item for item in kwargs.items() if item[1]]:
            question_id_str = re.match(r"\bquestion_([0-9]+)\b", k_key)
            if question_id_str and int(question_id_str.group(1)) in appointment_question_ids:
                partner_inputs[int(question_id_str.group(1))] = k_value
                continue
            checkbox_ids_str = re.match(r"\bquestion_([0-9]+)_answer_([0-9]+)\b", k_key)
            if checkbox_ids_str:
                question_id, answer_id = [int(checkbox_ids_str.group(1)), int(checkbox_ids_str.group(2))]
                if question_id in appointment_question_ids:
                    partner_inputs[question_id] = partner_inputs.get(question_id, []) + [answer_id]

        # The answer inputs will be created in _prepare_calendar_event_values from the values in answer_input_values
        answer_input_values = []
        base_answer_input_vals = {
            'appointment_type_id': appointment_type.id,
            'partner_id': customer.id,
        }
        description_bits = []
        description = ''

        if phone:
            description_bits.append(_('Phone: %s', phone))
        if email:
            description_bits.append(_('Email: %s', email))

        for question in appointment_type.question_ids.filtered(lambda question: question.id in partner_inputs.keys()):
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda answer: answer.id in partner_inputs[question.id])
                answer_input_values.extend([
                    dict(base_answer_input_vals, question_id=question.id, value_answer_id=answer.id) for answer in
                    answers
                ])
                description_bits.append(f'{question.name}: {", ".join(answers.mapped("name"))}')
            elif question.question_type in ['select', 'radio']:
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id,
                         value_answer_id=int(partner_inputs[question.id]))
                )
                selected_answer = question.answer_ids.filtered(
                    lambda answer: answer.id == int(partner_inputs[question.id]))
                description_bits.append(f'{question.name}: {selected_answer.name}')
            elif question.question_type == 'char':
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id,
                         value_text_box=partner_inputs[question.id].strip())
                )
                description_bits.append(f'{question.name}: {partner_inputs[question.id].strip()}')
            elif question.question_type == 'text':
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id,
                         value_text_box=partner_inputs[question.id].strip())
                )
                description_bits.append(f'{question.name}:<br/>{plaintext2html(partner_inputs[question.id].strip())}')

        if description_bits:
            description = f"<ul>{''.join(f'<li>{bit}</li>' for bit in description_bits)}</ul>"

        booking_line_values = []
        if appointment_type.schedule_based_on == 'resources':
            for resource in resources:
                resource_remaining_capacity = resources_remaining_capacity.get(resource)
                new_capacity_reserved = min(resource_remaining_capacity, asked_capacity, resource.capacity)
                asked_capacity -= new_capacity_reserved
                booking_line_values.append({
                    'appointment_resource_id': resource.id,
                    'capacity_reserved': new_capacity_reserved,
                    'capacity_used': new_capacity_reserved if resource.shareable and appointment_type.resource_manage_capacity else resource.capacity,
                })

        if invite_token:
            appointment_invite = request.env['appointment.invite'].sudo().search([('access_token', '=', invite_token)])
        else:
            appointment_invite = request.env['appointment.invite']
        vin_no = kwargs.get('vin_no') if kwargs.get('vin_no') else None
        if vin_no and len(vin_no) != 17:
            return request.redirect(
                '/appointment/%s?%s' % (appointment_type.id, keep_query('*')))
        event = request.env['calendar.event'].with_context(mail_notify_author=True,
                                                           mail_create_nolog=True,
                                                           mail_create_nosubscribe=True,
                                                           allowed_company_ids=staff_user.company_ids.ids,
                                                           ).sudo().create({
            'appointment_answer_input_ids': [Command.create(vals) for vals in answer_input_values],
            **appointment_type._prepare_calendar_event_values(
                asked_capacity, booking_line_values, description, duration,
                appointment_invite, guests, name, customer, staff_user, date_start, date_end)})

        vehicle_info = {
            'vehicle_brand_id': int(kwargs.get('brand_id')) if kwargs.get('brand_id') else None,
            'vehicle_model_id': int(kwargs.get('model_id')) if kwargs.get('model_id') and not kwargs.get(
                'model_id') == 'selected' else None,
            'vin_no': kwargs.get('vin_no'),
        }
        if vehicle_info:
            event.write(vehicle_info)
        return request.redirect(
            f"/calendar/view/{event.access_token}?partner_id={customer.id}&{keep_query('*', state='new')}")
