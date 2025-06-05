from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import urllib.parse


class VehicleAppointmentType(models.Model):
    _inherit = 'appointment.type'


class VehicleAppointment(models.Model):
    _inherit = 'calendar.event'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Vehicle Details
    vehicle_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Vehicle Brand')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model',
                                       domain="[('brand_id','=',vehicle_brand_id)]")
    vin_no = fields.Char(string="VIN No.")
    color = fields.Char()
    registration_no = fields.Char()
    year = fields.Char()

    # Vehicle Service Details
    service_adviser_id = fields.Many2one(comodel_name='res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])

    technician_id = fields.Many2one('res.users', string="Technician",
                                    domain=lambda self: [('groups_id', '=', self.env.ref(
                                        'tk_vehicle_management.vehicle_technician').id)])

    # Lead Details
    vehicle_lead_id = fields.Many2one('crm.lead', string="Lead")

    # Appointment Miss Mail
    is_sent_mail_miss = fields.Boolean()

    # Whatsapp Reminder
    wh_week_send = fields.Boolean()
    wh_day_send = fields.Boolean()
    wh_miss_send = fields.Boolean()
    reschedule_url = fields.Char(string="Reschedule URL", compute='_compute_reschedule_url')

    # Customer Address
    address_area = fields.Char(string="Address/Area", related='appointment_booker_id.address_area', store=True,
                               readonly=False)

    # Booking Details
    checkin_id = fields.Many2one('vehicle.booking', string="Check-In No.")

    # Constrain
    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    # Compute
    @api.depends('access_token', 'appointment_booker_id')
    def _compute_reschedule_url(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = "#"
            access_token = self.env['calendar.attendee'].search(
                [('event_id', '=', rec.id), ('partner_id', '=', rec.appointment_booker_id.id)], limit=1).mapped(
                'access_token')
            if access_token:
                url = base_url + "/calendar/meeting/view?token=" + str(access_token[0]) + "&id=" + str(
                    rec.id)
            rec.reschedule_url = url

    def action_create_vehicle_service_lead(self):
        if not self.service_adviser_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Please select service adviser to create lead'),
                    'sticky': False,
                }}
        if not self.technician_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Please select technician to create lead'),
                    'sticky': False,
                }}
        lead_date = {
            # Appointment
            'name': self.name,
            'vehicle_appointment_id': self.id,
            'description': self.description,
            # Service Adviser
            'service_adviser_id': self.service_adviser_id.id,
            'technician_id': self.technician_id.id,
            # Responsible
            'user_id': self.user_id.id,
            # Customer Details
            'partner_id': self.appointment_booker_id.id,
            'address_area': self.address_area,
            # Vehicle Details
            'vehicle_model_id': self.vehicle_model_id.id,
            'brand_id': self.vehicle_brand_id.id,
            'vin_no': self.vin_no,
            'vehicle_color': self.color,
            'year': self.year,
            'registration_no': self.registration_no,
        }
        lead_id = self.env['crm.lead'].create(lead_date)
        self.vehicle_lead_id = lead_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead',
            'res_model': 'crm.lead',
            'res_id': self.vehicle_lead_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_create_vehicle_checkin(self):
        if not self.service_adviser_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Please select service adviser to create lead'),
                    'sticky': False,
                }}
        if not self.technician_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Please select technician to create lead'),
                    'sticky': False,
                }}
        booking_data = {
            # Appointment
            'vehicle_appointment_id': self.id,
            # Customer
            'customer_id': self.appointment_booker_id.id,
            'address_area': self.address_area,
            # Vehicle Details
            'vehicle_model_id': self.vehicle_model_id.id,
            'brand_id': self.vehicle_brand_id.id,
            'vin_no': self.vin_no,
            'color': self.color,
            'year': self.year,
            'registration_no': self.registration_no,
            # Service Adviser
            'service_adviser_id': self.service_adviser_id.id,
            'sale_person_id': self.user_id.id,
            # Booking Source
            'booking_source': 'other',
            'other_source': 'Appointment'
        }
        checkin_id = self.env['vehicle.booking'].create(booking_data)
        self.checkin_id = checkin_id.id
        self.checkin_id.action_send_booking_whatsapp_message(send_to='service_adviser')
        self.checkin_id.action_send_booking_whatsapp_message(send_to='customer')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Check-in',
            'res_model': 'vehicle.booking',
            'res_id': self.checkin_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_vehicle_lead(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead',
            'res_model': 'crm.lead',
            'res_id': self.vehicle_lead_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_vehicle_checkin(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Check-in',
            'res_model': 'vehicle.booking',
            'res_id': self.checkin_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    # Scheduler
    @api.model
    def vehicle_appointment_miss_mail_send(self):
        mail_template = self.env.ref('tk_vehicle_management.service_appointment_miss_mail_template')
        today_date = fields.Datetime.now()
        appointments = self.env['calendar.event'].search([('is_sent_mail_miss', '=', False), ('stop', '<', today_date)])
        for rec in appointments:
            if mail_template:
                mail_template.send_mail(rec.id, force_send=True)
            rec.is_sent_mail_miss = True

    @api.model
    def wa_send_vehicle_appointment_week_reminder(self):
        wa_template_id = self.get_whatsapp_template(
            template_id='tk_vehicle_management.wa_template_appointment_reminder_week_id')
        if wa_template_id:
            today_date = fields.Date.today()
            appointments = self.env['calendar.event'].search([('wh_week_send', '=', False)])
            for rec in appointments:
                week_date = rec.start.date() - relativedelta(days=15)
                if today_date == week_date and wa_template_id:
                    mobile_no = rec.check_whatsapp_phone(rec.appointment_booker_id)
                    if mobile_no:
                        rec.action_send_whatsapp_message(mobile_no, wa_template_id)
                        rec.wh_week_send = True

    @api.model
    def wa_send_vehicle_appointment_day_reminder(self):
        wa_template_id = self.get_whatsapp_template(
            template_id='tk_vehicle_management.wa_template_appointment_reminder_day_id')
        if wa_template_id:
            today_date = fields.Date.today()
            appointments = self.env['calendar.event'].search([('wh_day_send', '=', False)])
            for rec in appointments:
                day_date = rec.start.date() - relativedelta(days=1)
                if today_date == day_date and wa_template_id:
                    mobile_no = rec.check_whatsapp_phone(rec.appointment_booker_id)
                    if mobile_no:
                        rec.action_send_whatsapp_message(mobile_no, wa_template_id)
                        rec.wh_day_send = True

    @api.model
    def wa_send_vehicle_appointment_miss_reminder(self):
        wa_template_id = self.get_whatsapp_template(
            template_id='tk_vehicle_management.wa_template_appointment_miss_id')
        if wa_template_id:
            today_date = fields.Datetime.now()
            appointments = self.env['calendar.event'].search([('wh_miss_send', '=', False), ('stop', '<', today_date)])
            for rec in appointments:
                mobile_no = rec.check_whatsapp_phone(rec.appointment_booker_id)
                if mobile_no:
                    rec.action_send_whatsapp_message(mobile_no, wa_template_id)
                    rec.wh_miss_send = True

    def get_whatsapp_template(self, template_id):
        wa_template_id = False
        config_template_id = self.env['ir.config_parameter'].sudo().get_param(template_id)
        if config_template_id:
            wa_template_id = self.env['whatsapp.template'].sudo().browse(int(config_template_id))
        return wa_template_id

    def action_send_whatsapp_message(self, phone, wa_template_id):
        body = self._get_html_preview_whatsapp(wa_template_id, self)
        post_values = {'body': body,
                       'message_type': 'whatsapp_message',
                       'partner_ids': [self.env.user.partner_id.id], }
        message = self.env['mail.message'].create(dict(post_values, res_id=self.id, model=wa_template_id.model,
                                                       subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                                           "mail.mt_note")))
        message = self.env['whatsapp.message'].sudo().create({
            'mobile_number': phone,
            'wa_template_id': wa_template_id.id,
            'wa_account_id': wa_template_id.wa_account_id.id,
            'mail_message_id': message.id,
        })
        message._send(force_send_by_cron=True)

    def check_whatsapp_phone(self, partner_id):
        mobile_no = False
        if partner_id.mobile:
            mobile_no = partner_id.mobile
        elif partner_id.phone:
            mobile_no = partner_id.phone
        return mobile_no

    def _get_html_preview_whatsapp(self, wa_template_id, rec):
        """This method is used to get the html preview of the whatsapp message."""
        self.ensure_one()
        # No of Text
        number_of_free_text = len(wa_template_id.variable_ids.filtered(
            lambda line: line.field_type == 'free_text' and line.line_type == 'body'))
        # Header Text
        header_text_1 = False
        if wa_template_id.header_type == 'text':
            header_params = wa_template_id.variable_ids.filtered(lambda line: line.line_type == 'header')
            if wa_template_id.variable_ids and header_params:
                header_param = header_params[0]
                if header_param.field_type == 'free_text' and not header_text_1:
                    header_text_1 = header_param.demo_value
        # Prepare Body
        template_variables_value = wa_template_id.variable_ids._get_variables_value(rec)
        text_vars = wa_template_id.variable_ids.filtered(lambda var: var.field_type == 'free_text')
        for var_index, body_text_var in zip(range(1, number_of_free_text + 1),
                                            text_vars.filtered(lambda var: var.line_type == 'body')):
            free_text_x = self[f'free_text_{var_index}']
            if free_text_x:
                template_variables_value[f'body-{body_text_var.name}'] = free_text_x
        if header_text_1 and text_vars.filtered(lambda var: var.line_type == 'header'):
            template_variables_value['header-{{1}}'] = self.header_text_1
        return wa_template_id._get_formatted_body(variable_values=template_variables_value)
