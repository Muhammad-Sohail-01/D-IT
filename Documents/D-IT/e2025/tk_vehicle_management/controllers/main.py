import base64
import logging
from markupsafe import Markup
from odoo import fields, SUPERUSER_ID, api
from odoo.http import request, route
from odoo import http, tools, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import translate_attrib_value

_logger = logging.getLogger(__name__)


def get_quotation_url(access_token=None):
    url = '/'
    if access_token:
        url = '/vehicle-service/job-card/' + access_token + '/'
    return url


def validate_mandatory_fields(mandate_fields, kw):
    """To validate mandatory fields"""
    error, data = None, {}
    for key, value in mandate_fields.items():
        if not kw.get(key):
            error = "Mandatory fields " + value + " Missing"
            break
        else:
            data[key] = kw.get(key)
    return error, data


def check_service_part_confirmation(data):
    error = None
    for key in data.keys():
        if error:
            break
        if key != 'access_token':
            try:
                int_key = int(key)  # Try converting the key to an integer
            except ValueError as e:
                _logger.warning(e)
                error = True
    return error


def get_user_error(type):
    error = {
        'not_access_token': {
            'type': 'warning',
            'title': 'Invalid URL !',
            'message': """Sorry, but this url is invalid.
                          If you continue to encounter issues, reach out to support for assistance."""
        },
        'invalid_token': {
            'type': 'danger',
            'title': 'Invalid URL !',
            'message': """The URL you are accessing is invalid. Please re-open the quotation link from the email.
                          If you continue to encounter issues, reach out to support for assistance."""
        },
        'quotation_expired': {
            'type': 'danger',
            'title': 'Quotation Expired!',
            'message': """Your quotation has expired. Please click on 'Request for reopen quotation' to 
                          send a request for reopening. Thank you."""
        },
        'quotation_reject': {
            'type': 'danger',
            'title': 'Quotation Rejected!',
            'message': """Your decision to reject quotation has been noted. Click on 'Request for reopen quotation'
                          to send a request for reopening. Thank you."""
        },
        'quote_cancel': {
            'type': 'danger',
            'title': 'Quotation Cancelled!',
            'message': """Your decision to cancel quotation has been noted. Click on 'Request for reopen quotation' 
                          to send a request for reopening. Thank you."""
        },
        'request_submit': {
            'type': 'success',
            'title': 'Quotation Reopen Request Submitted!',
            'message': """Quotation reopen request submitted. You will be notified via email once 
                          the request has been approved."""
        },
        'quote_cancel_additional_part': {
            'type': 'danger',
            'title': 'Additional Part Quotation Cancelled!',
            'message': """Your decision to cancel quotation has been noted. Thank you."""
        },
        'quotation_expired_additional_part': {
            'type': 'warning',
            'title': 'Additional Part Quotation Expired!',
            'message': """Your quotation has expired. if you still need to approve additional part please 
                    contact support for further assistance."""
        },
        # Consent Error
        'consent_invalid_token': {
            'type': 'danger',
            'title': 'Invalid URL !',
            'message': """The URL you are accessing is invalid. Please re-open the approval link from the 
                        message or email, If you continue to encounter issues, reach out to support for assistance."""
        },
        'consent_request_submit': {
            'type': 'success',
            'title': 'Approval Reopen Request Submitted!',
            'message': """Approval reopen request submitted. You will be notified via email/message once 
                            the request has been approved."""
        },
        'consent_expired': {
            'type': 'warning',
            'title': 'Approval Expired!',
            'message': """Customer approval has expired. Please click on 'Request for reopen' to 
                              send a request for reopening. Thank you."""
        },
        'consent_reject': {
            'type': 'danger',
            'title': 'Approval Rejected!',
            'message': """Your decision to reject approval has been noted. Click on 'Request for reopen'
                              to send a request for reopening. Thank you."""
        },
    }
    return error.get(type)


def send_quotation_user_action_mail(values):
    inspection_id = values.get('inspection_id')
    template_id = request.env.ref(
        'tk_vehicle_management.customer_quotation_action_part_mail_template').sudo()
    email_values = {
        'email_to': values.get('email_to'),
        'email_from': values.get('email_from'),
        'subject': values.get('subject'),
        'author_id': values.get('author_id'),
    }
    ctx = {
        'type': values.get('type'),
        'for': values.get('for'),
        'reject_reason': values.get('reject_reason')
    }
    request.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(
        inspection_id,
        email_values=email_values,
        force_send=True)


def handle_quote_state(inspection_id):
    quote_state = inspection_id.quote_state
    quot_reopen_request = inspection_id.quot_reopen_request
    error_type = None
    if quot_reopen_request in ['draft', False]:
        if quote_state == 'expire':
            error_type = 'quotation_expired'
        elif quote_state == 'reject':
            error_type = 'quotation_reject'
        elif quote_state == 'cancel':
            error_type = 'quote_cancel'
    else:
        error_type = 'request_submit'
    return error_type


class VehicleServiceQuotation(http.Controller):
    @http.route(["/vehicle-service/job-card/", "/vehicle-service/job-card/<string:access_token>"],
                type='http',
                auth="public", website=True)
    def user_quotation(self, access_token=None, **kw):
        quotation_template = 'tk_vehicle_management.user_quot_details'
        quot_term = request.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.quot_term')
        inspection_obj = request.env['vehicle.inspection'].sudo()
        values = {}
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(quotation_template, values)
        # Check Inspection Record
        inspection_id = inspection_obj.search([('access_token', '=', access_token)], limit=1)
        if not inspection_id:
            values['error'] = get_user_error('invalid_token')
            return request.render(quotation_template, values)
        values['inspection_id'] = inspection_id
        # Check Quotation Status
        if inspection_id.quote_state in ['expire', 'reject', 'cancel']:
            values['error'] = get_user_error(handle_quote_state(inspection_id))
            return request.render(quotation_template, values)
        values['quot_term'] = quot_term if quot_term else False
        return request.render(quotation_template, values)

    @http.route('/vehicle-service/<string:type>/<string:token>/<string:report>', type='http',
                auth='public')
    def user_job_card_report(self, token, type, report):
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', token)])
        if not inspection_id:
            return request.redirect('/')
        if type == 'job-card-report' and report == 'Job-Card-PDF':
            pdf_data = "tk_vehicle_management.vehicle_inspection_report_service_part_qweb"
            record_id = inspection_id.vehicle_health_report_id.id
            file_name = "Job Card.pdf"
        if type == 'scratch-report' and report == 'Scratch-Report-PDF':
            pdf_data = "tk_vehicle_management.action_inspection_scratch_report"
            record_id = inspection_id.id
            file_name = "Scratch Report.pdf"
        if type == 'concern-report' and report == 'Concern-Report-PDF':
            pdf_data = "tk_vehicle_management.action_vehicle_inspection_concern_qweb_report"
            record_id = inspection_id.id
            file_name = "Approval-Report.pdf"
        if type == 'quot-report' and report == 'Quotation-Report-PDF':
            pdf_data = "tk_vehicle_management.action_vehicle_quot_inspection_qweb_report"
            record_id = inspection_id.id
            file_name = "Quotation-Report.pdf"
        if type == 'updated-quot' and report == 'Updated-Repair-Estimate-Report-PDF':
            pdf_data = "tk_vehicle_management.action_vehicle_quot_update_inspection_qweb_report"
            record_id = inspection_id.id
            file_name = "Updated-Repair-Estimate-Report.pdf"
        pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(pdf_data, record_id)
        response = request.make_response(pdf_content, headers=[('Content-Type', 'application/pdf')])
        response.headers.add('Content-Disposition',
                             'inline; filename="%s"' % inspection_id.name + file_name)
        return response


    @http.route('/vehicle-service/job-card/submit-quot/part', type='http', auth='public')
    def job_card_quot_service_spare_parts(self, **kw):
        selected_parts = []
        url = get_quotation_url(access_token=kw.get('access_token'))
        if not kw:
            return request.redirect(url)
    
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', kw.get('access_token'))])
        part_obj = request.env['vehicle.required.parts'].sudo()
    
        # User Selected Parts
        selected_parts = [int(key) for key, value in kw.items() if key != 'access_token' and value == 'on']
    
        # Default + User Selected Parts
        user_parts_ids = selected_parts + part_obj.search([
            ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
            ('active', '=', True), ('part_selected', '=', True)]).mapped('id')
        user_selected_part_ids = part_obj.browse(user_parts_ids)
    
        # Update Selected Parts
        user_selected_part_ids.write({'part_selected': True})
    
        # Deactivate Not Selected Parts
        part_to_deactivate = part_obj.search([
            ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
            ('id', 'not in', list(user_parts_ids)), ('display_type', '=', False)
        ])
        part_to_deactivate.write({'active': False})
        inspection_id.part_selected = True
    
        # Logic for Removing Unselected Parts from Sale Order
        sale_orders = request.env['sale.order'].sudo().search([
            ('job_card_id', '=', inspection_id.id),  # Assuming the relation to inspection
            ('state', '=', 'sent')  # Ensure the sale order is still in draft state
        ])
    
        for sale_order in sale_orders:
            # Fetch the sale order lines related to unselected parts
            for order_line in sale_order.order_line:
                if order_line.product_id.id in part_to_deactivate.mapped('product_id.id'):
                    # Unlink the product (order line) from the sale order
                    order_line.unlink()
    
        return request.redirect(url)


    @http.route('/vehicle-service/job-card/submit-quot/service', type='http', auth='public')
    def job_card_quot_service(self, **kw):
        selected_services = []
        url = get_quotation_url(access_token=kw.get('access_token'))
        if not kw:
            return request.redirect(url)
    
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', kw.get('access_token'))])
        services_obj = request.env['vehicle.required.services'].sudo()
    
        # User Selected Services
        selected_services = [int(key) for key, value in kw.items() if key != 'access_token' and value == 'on']
    
        # Default + User Selected Services
        user_services_ids = selected_services + services_obj.search([
            ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
            ('active', '=', True), ('service_selected', '=', True)]).mapped('id')
        user_selected_service_ids = services_obj.browse(user_services_ids)
    
        # Update Selected Services
        user_selected_service_ids.write({'service_selected': True})
    
        # Deactivate Not Selected Services
        services_to_deactivate = services_obj.search([
            ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
            ('id', 'not in', list(user_services_ids)), ('display_type', '=', False)])
        services_to_deactivate.write({'active': False})
        inspection_id.service_selected = True
    
        # Logic for Removing Unselected Services from Sale Order
        sale_orders = request.env['sale.order'].sudo().search([
            ('job_card_id', '=', inspection_id.id),  # Assuming the relation to inspection
            ('state', '=', 'sent')  # Ensure the sale order is still in draft state
        ])
    
        for sale_order in sale_orders:
            # Fetch the sale order lines related to unselected services
            for order_line in sale_order.order_line:
                if order_line.product_id.id in services_to_deactivate.mapped('product_id.id'):
                    # Unlink the product (order line) from the sale order
                    order_line.unlink()
    
        return request.redirect(url)


    # @http.route('/vehicle-service/job-card/submit-quot/service', type='http', auth='public')
    # def job_card_quot_service(self, **kw):
    #     selected_services = []
    #     url = get_quotation_url(access_token=kw.get('access_token'))
    #     if not kw:
    #         return request.redirect(url)

    #     inspection_id = request.env['vehicle.inspection'].sudo().search(
    #         [('access_token', '=', kw.get('access_token'))])
    #     services_obj = request.env['vehicle.required.services'].sudo()

    #     # Default Selected Services
    #     # default_selected_services = services_obj.search([
    #     #     ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #     #     ('required_status', '=', 'must_required'),
    #     #     ('active', '=', True)
    #     # ]).mapped('id')

    #     # User Selected Service
    #     selected_services = [int(key) for key, value in kw.items() if
    #                          key != 'access_token' and value == 'on']

    #     # Default + User Selected Service
    #     user_services_ids = selected_services + services_obj.search([
    #         ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #         ('active', '=', True), ('service_selected', '=', True)]).mapped('id')
    #     user_selected_service_ids = services_obj.browse(user_services_ids)

    #     # Update Selected Services
    #     user_selected_service_ids.write({'service_selected': True})

    #     # Deactivate Not Selected Service
    #     services_to_deactivate = services_obj.search([
    #         ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #         ('id', 'not in', list(user_services_ids)), ('display_type', '=', False)])
    #     services_to_deactivate.write({'active': False})
    #     inspection_id.service_selected = True
    #     return request.redirect(url)


    # @http.route('/vehicle-service/job-card/submit-quot/part', type='http', auth='public')
    # def job_card_quot_service_spare_parts(self, **kw):
    #     selected_parts = []
    #     url = get_quotation_url(access_token=kw.get('access_token'))
    #     if not kw:
    #         return request.redirect(url)
    #     inspection_id = request.env['vehicle.inspection'].sudo().search(
    #         [('access_token', '=', kw.get('access_token'))])
    #     part_obj = request.env['vehicle.required.parts'].sudo()

    #     # Default Selected Parts
    #     # default_selected_parts = part_obj.search([
    #     #     ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #     #     ('required_status', '=', 'must_required'),
    #     #     ('active', '=', True)
    #     # ]).mapped('id')

    #     # User Selected Parts
    #     selected_parts = [int(key) for key, value in kw.items() if
    #                       key != 'access_token' and value == 'on']

    #     # Default + User Selected Service
    #     user_parts_ids = selected_parts + part_obj.search([
    #         ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #         ('active', '=', True), ('part_selected', '=', True)]).mapped('id')
    #     user_selected_part_ids = part_obj.browse(user_parts_ids)

    #     # Update Selected Services
    #     user_selected_part_ids.write({'part_selected': True})

    #     # Deactivate Not Selected Service
    #     part_to_deactivate = part_obj.search([
    #         ('vehicle_health_report_id', '=', inspection_id.vehicle_health_report_id.id),
    #         ('id', 'not in', list(user_parts_ids)), ('display_type', '=', False)
    #     ])
    #     part_to_deactivate.write({'active': False})
    #     inspection_id.part_selected = True

    #     return request.redirect(url)

    @http.route(["/vehicle/job-card/quotation/<string:access_token>/accept"], type='json',
                auth="public", website=True)
    def job_card_quote_accept(self, access_token=None, **kw):
        redirect_url = "/vehicle-service/job-card/%s" % access_token
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', access_token)]
        )

    
        inspection_id.write({
        'signature': kw.get('signature'),
        'quote_state': 'signed',
        'quote_accept_date_time': fields.Datetime.now(),
        'status': 'approve'
        })
        if inspection_id.sale_order_id:
            inspection_id.sale_order_id.action_confirm()

    # Send Mail
        emails = [inspection_id.service_adviser_id.partner_id.email,
                  inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': inspection_id.company_id.partner_id.id,
            'inspection_id': inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Quotation Confirmed and Signed by Customer',
            'type': 'accepted',
            'for': 'quotation',
            'reject_reason': None
        })

        return {
            'force_refresh': True,
            'redirect_url': redirect_url,
        }


    @http.route(["/vehicle-service/job-card/reopen-request/<string:access_token>"], type='http',
                auth="public",
                website=True)
    def user_quotation_quote_reopen_request(self, access_token=None, **kw):
        redirect_url = "/vehicle-service/job-card/%s" % access_token
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', access_token)], limit=1)
        if inspection_id.quote_state == 'expire':
            inspection_id.write({'quot_reopen_request': 'reopen_expire'})
        if inspection_id.quote_state == 'reject':
            inspection_id.write({'quot_reopen_request': 'reopen_reject'})
        if inspection_id.quote_state == 'cancel':
            inspection_id.write({'quot_reopen_request': 'reopen_cancel'})
        return request.redirect(redirect_url)

    @http.route('/vehicle-service/job-card/quot-reject/reason', type='http', auth='public')
    def job_card_quot_reject(self, reject_reason=None, access_token=None, **kw):
        url = get_quotation_url(access_token=access_token)
        if not access_token:
            return request.redirect(url)
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', access_token)], limit=1)
        if reject_reason:
            inspection_id.write({
                'quote_reject_reason': reject_reason,
                'quote_state': 'reject'
            })
        # Send Mail
        emails = [inspection_id.service_adviser_id.partner_id.email,
                  inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': inspection_id.company_id.partner_id.id,
            'inspection_id': inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Quotation Rejected by Customer',
            'type': 'rejected',
            'for': 'quotation',
            'reject_reason': reject_reason
        })
        return request.redirect(url)

    @http.route('/vehicle-service/job-card/quot-cancel/<string:access_token>', type='http',
                auth='public')
    def job_card_quot_cancel(self, access_token=None, **kw):
        url = get_quotation_url(access_token=access_token)
        if not access_token:
            return request.redirect(url)
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('access_token', '=', access_token)], limit=1)
        inspection_id.quote_state = 'cancel'
        # Send Mail
        emails = [inspection_id.service_adviser_id.partner_id.email,
                  inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': inspection_id.company_id.partner_id.id,
            'inspection_id': inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Quotation Cancelled by Customer',
            'type': 'cancelled',
            'for': 'quotation',
            'reject_reason': None
        })
        return request.redirect(url)

    # Additional Part Quotation
    @http.route(["/vehicle-service/job-card/additional-part/",
                 "/vehicle-service/job-card/additional-part/<string:access_token>", ],
                type='http', auth="public", website=True)
    def user_additional_part(self, access_token=None, **kw):
        quotation_template = 'tk_vehicle_management.user_quot_additional_part_details'
        quot_term = request.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.quot_term')
        part_obj = request.env['additional.part.confirmation'].sudo()
        values = {}
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(quotation_template, values)
        # Check Inspection Record
        additional_parts = part_obj.search([('access_token', '=', access_token)], limit=1)
        if not additional_parts:
            values['error'] = get_user_error('invalid_token')
            return request.render(quotation_template, values)
        if additional_parts.quote_state == 'cancel':
            values['error'] = get_user_error('quote_cancel_additional_part')
            return request.render(quotation_template, values)
        if additional_parts.quote_state == 'expire':
            values['error'] = get_user_error('quotation_expired_additional_part')
            return request.render(quotation_template, values)
        values['additional_part'] = additional_parts
        values['quot_term'] = quot_term if quot_term else False
        values['confirmation_error'] = False
        return request.render(quotation_template, values)

    @http.route('/vehicle-service/job-card/additional-part/submit',
                type='http',
                auth='public')
    def user_additional_spare_parts(self, **kw):
        """Existing Services Additional Part """
        url = '/'
        if not kw:
            return request.redirect(url)
        if kw.get('access_token'):
            url = '/vehicle-service/job-card/additional-part/' + kw.get('access_token') + '/'
        # Part Confirmation
        part_obj = request.env['vehicle.required.parts'].sudo()
        additional_part_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', kw.get('access_token'))],
            limit=1)
        existing_parts = additional_part_id.additional_part_ids.filtered(
            lambda line: line.service_id.service_selected)

        # User Selected Part
        for key, value in kw.items():
            if not key == 'access_token':
                if value == 'on':
                    part_id = part_obj.browse(int(key))
                    part_id.additional_part_selected = True
        additional_part_id.confirm_selection = True

        # Remove all Remaining Part
        for d in existing_parts:
            if not d.additional_part_selected:
                d.additional_part_rejected = True
        return request.redirect(url)

    @http.route('/vehicle-service/job-card/additional-service/submit',
                type='http',
                auth='public')
    def user_additional_services(self, **kw):
        """Newly Added Additional Services """
        url = '/'
        if not kw:
            return request.redirect(url)
        if kw.get('access_token'):
            url = '/vehicle-service/job-card/additional-part/' + kw.get('access_token') + '/'
        # Service Confirmation
        service_obj = request.env['vehicle.required.services'].sudo()
        additional_part_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', kw.get('access_token'))], limit=1)
        error = check_service_part_confirmation(kw)
        if error:
            return request.redirect("/")

        # User Selected Part
        for key, value in kw.items():
            if not key == 'access_token' and value == 'on':
                service_id = service_obj.browse(int(key))
                service_id.additional_service_selected = True

        # Confirm Service Selection
        additional_part_id.confirm_selection_service = True

        # Remove Extra Service
        for service in additional_part_id.additional_service_ids:
            if not service.additional_service_selected:
                service.service_rejected = True

        # If any service has not part Skip Additional Service parts
        is_any_additional_service_part = additional_part_id.additional_part_ids.filtered(
            lambda line: line.service_id.id in additional_part_id.additional_service_ids.ids)
        if not is_any_additional_service_part:
            additional_part_id.confirm_selection_service_part = True

        return request.redirect(url)

    @http.route('/vehicle-service/job-card/additional-service-part/submit',
                type='http',
                auth='public')
    def user_additional_services_parts(self, **kw):
        """Newly Additional Services  Parts"""
        url = '/'
        if not kw:
            return request.redirect(url)
        if kw.get('access_token'):
            url = '/vehicle-service/job-card/additional-part/' + kw.get('access_token') + '/'
        error = check_service_part_confirmation(kw)
        if error:
            return request.redirect("/")
        # Service Confirmation
        part_obj = request.env['vehicle.required.parts'].sudo()
        additional_part_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', kw.get('access_token'))], limit=1)
        service_parts = additional_part_id.additional_part_ids.filtered(
            lambda line: line.service_id.id in additional_part_id.additional_service_ids.ids)

        # User Selected Part
        for key, value in kw.items():
            if not key == 'access_token' and value == 'on':
                part_id = part_obj.browse(int(key))
                part_id.additional_part_selected = True

        # Confirm Service - Part Selection
        additional_part_id.confirm_selection_service_part = True

        # Remove Extra Service
        for part in service_parts:
            if not part.additional_part_selected:
                part.additional_part_rejected = True

        return request.redirect(url)

    @http.route(["/vehicle/job-card/additional-part/quotation/<string:access_token>/accept"],
                type='json',
                auth="public", website=True)
    def job_card_additional_part_quote_accept(self, access_token=None, **kw):
        redirect_url = '/vehicle-service/job-card/additional-part/' + access_token + '/'
        additional_part_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', access_token)], limit=1)
        additional_part_id.write({
            'signature': kw.get('signature'),
            'quote_state': 'signed',
            'quote_accept_date_time': fields.Datetime.now()
        })
        for service in additional_part_id.additional_service_ids:
            if service.additional_service_selected:
                service.action_approve_additional_service()
            if service.service_rejected:
                service.action_reject_additional_service()
        for d in additional_part_id.additional_part_ids:
            if d.additional_part_selected:
                d.action_approve_part()
            if d.additional_part_rejected:
                d.action_reject_part_user()

        # Send Mail
        emails = [additional_part_id.inspection_id.service_adviser_id.partner_id.email,
                  additional_part_id.inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': additional_part_id.inspection_id.company_id.partner_id.id,
            'inspection_id': additional_part_id.inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Additional Part Quotation Confirmed and Signed by Customer',
            'type': 'accepted',
            'for': 'additional part quotation',
            'reject_reason': None
        })
        return {
            'force_refresh': True,
            'redirect_url': redirect_url,
        }

    @http.route(
        ["/vehicle-service/job-card/additional-part/quotation/<string:access_token>/cancel"],
        type='http',
        auth="public", website=True)
    def job_card_additional_part_quote_cancel(self, access_token=None, **kw):
        redirect_url = '/vehicle-service/job-card/additional-part/' + access_token + '/'
        additional_part_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', access_token)], limit=1)
        additional_part_id.quote_state = 'cancel'
        for service in additional_part_id.additional_service_ids:
            service.service_rejected = True
            service.action_reject_additional_service()
        for d in additional_part_id.additional_part_ids:
            if d.additional_part_selected:
                d.additional_part_selected = False
                d.additional_part_rejected = True
            if d.additional_part_rejected:
                d.action_reject_part_user()
        # Send Mail
        emails = [additional_part_id.inspection_id.service_adviser_id.partner_id.email,
                  additional_part_id.inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': additional_part_id.inspection_id.company_id.partner_id.id,
            'inspection_id': additional_part_id.inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Additional Part Quotation Cancelled by Customer',
            'type': 'cancelled',
            'for': 'additional part quotation',
            'reject_reason': None
        })
        return request.redirect(redirect_url)

    # Portal Job Card Tree
    @http.route(['/my/vehicle', '/my/vehicle/<string:type>'], type='http', auth="user",
                website=True)
    def portal_vehicle_tree(self, type=None, **kwargs):
        inspection_obj = request.env['vehicle.inspection'].sudo()
        template = None
        values = {}
        domain = [('customer_id', '=', request.env.user.partner_id.id)]
        if not type or type not in ['jc-updated-quot', 'job-card-quot', 'vehicle-warranty',
                                    'registered-vehicle',
                                    'job-cards']:
            return request.redirect('/my')
        if type == 'job-cards':
            job_cards = inspection_obj.search(domain)
            values = {
                'job_cards': job_cards,
                'page_name': 'portal_job_card_view_tree'
            }
            template = "tk_vehicle_management.portal_my_job_card"
        if type == 'registered-vehicle':
            vehicles = request.env['register.vehicle'].sudo().search(domain)
            values = {
                'vehicles': vehicles,
                'page_name': 'portal_register_vehicle_view_tree'
            }
            template = "tk_vehicle_management.portal_my_register_vehicle"
        if type == 'vehicle-warranty':
            warranties = request.env['vehicle.warranty'].sudo().search(domain)
            values = {
                'warranties': warranties,
                'page_name': 'portal_vehicle_warranty_view_tree'
            }
            template = "tk_vehicle_management.portal_my_vehicles_warranty"
        if type == 'job-card-quot':
            vehicle_quot = inspection_obj.search(domain)
            values = {
                'vehicle_quot': vehicle_quot,
                'page_name': 'portal_job_card_quot_view_tree'
            }
            template = "tk_vehicle_management.portal_my_vehicle_quotation"
        if type == 'jc-updated-quot':
            job_card_ids = inspection_obj.search(domain).mapped('id')
            additional_part_quot = request.env['additional.part.confirmation'].sudo().search(
                [('inspection_id', 'in', job_card_ids)])
            values = {
                'jc_update_quot': additional_part_quot,
                'page_name': 'portal_jc_update_quot_view_tree'
            }
            template = "tk_vehicle_management.portal_my_vehicle_update_quotation"
        return request.render(template, values)

    @http.route(['/my/vehicle/<string:filter_by>/<string:access_token>'], type='http', auth="user",
                website=True)
    def portal_vehicle_tree_filtered(self, filter_by=None, access_token=None, **kwargs):
        template = None
        values = {}
        inspection_obj = request.env['vehicle.inspection'].sudo()
        domain = [('customer_id', '=', request.env.user.partner_id.id)]
        if filter_by == 'filter-revised':
            inspection_id = inspection_obj.search([('access_token', '=', access_token)], limit=1)
            job_card_ids = inspection_obj.search(domain).mapped('id')
            additional_part_quot = request.env['additional.part.confirmation'].sudo().search(
                [('inspection_id', 'in', job_card_ids), ('inspection_id', '=', inspection_id.id)], )
            values = {
                'jc_update_quot': additional_part_quot,
                'page_name': 'portal_jc_update_quot_view_tree'
            }
            template = "tk_vehicle_management.portal_my_vehicle_update_quotation"
        if filter_by == 'filter-warranty':
            vehicles = request.env['register.vehicle'].sudo().search(
                [('access_token', '=', access_token)] + domain,
                limit=1).mapped('id')
            warranties = request.env['vehicle.warranty'].sudo().search(
                [('register_vehicle_id', 'in', vehicles)])
            values = {
                'warranties': warranties,
                'page_name': 'portal_vehicle_warranty_view_tree'
            }
            template = "tk_vehicle_management.portal_my_vehicles_warranty"
        return request.render(template, values)

    # Portal Job Card Form
    @http.route(['/my/vehicle/job-cards/form',
                 '/my/vehicle/job-cards/form/<string:access_token>'], type='http', auth="user",
                website=True)
    def portal_job_card_form(self, access_token=None, **kw):
        inspection_obj = request.env['vehicle.inspection'].sudo()
        template = "tk_vehicle_management.portal_my_job_card_form"
        values = {
            'page_name': 'portal_job_card_view_form'
        }
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(template, values)
        # Check Inspection Record
        job_card_id = inspection_obj.search([('access_token', '=', access_token)], limit=1)
        if not job_card_id:
            values['error'] = get_user_error('invalid_token')
            return request.render(template, values)
        values['job_card_id'] = job_card_id
        return request.render(template, values)

    # Portal Register Vehicle
    @http.route(['/my/vehicle/registered-vehicle/form',
                 '/my/vehicle/registered-vehicle/form/<string:access_token>'], type='http',
                auth="user",
                website=True)
    def portal_register_vehicle_form(self, access_token=None, **kw):
        template = "tk_vehicle_management.portal_my_register_vehicle_form"
        values = {
            'page_name': 'portal_register_vehicle_view_form'
        }
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(template, values)
        # Check Record
        register_vehicle_id = request.env['register.vehicle'].sudo().search(
            [('access_token', '=', access_token)],
            limit=1)
        if not register_vehicle_id:
            values['error'] = get_user_error('invalid_token')
            return request.render(template, values)
        values['register_vehicle_id'] = register_vehicle_id
        return request.render(template, values)

    # Portal Vehicle Warranty
    @http.route(['/my/vehicle/vehicle-warranty/form',
                 '/my/vehicle/vehicle-warranty/form/<string:access_token>'], type='http',
                auth="user",
                website=True)
    def portal_vehicle_warranty_form(self, access_token=None, **kw):
        template = "tk_vehicle_management.portal_my_vehicles_warranty_form"
        values = {
            'page_name': 'portal_vehicle_warranty_view_form'
        }
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(template, values)
        # Check Record
        warranty_id = request.env['vehicle.warranty'].sudo().search(
            [('access_token', '=', access_token)],
            limit=1)
        if not warranty_id:
            values['error'] = get_user_error('invalid_token')
            return request.render(template, values)
        values['warranty_id'] = warranty_id
        return request.render(template, values)

    # Portal Job Card Revised Quotation
    @http.route(['/my/vehicle/jc-updated-quot/form',
                 '/my/vehicle/jc-updated-quot/form/<string:access_token>'], type='http',
                auth="user",
                website=True)
    def portal_jc_updated_quot_form(self, access_token=None, **kw):
        template = "tk_vehicle_management.portal_my_vehicle_update_quotation_form"
        values = {
            'page_name': 'portal_jc_updated_quot_view_form'
        }
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(template, values)
        # Check Record
        revised_quot_id = request.env['additional.part.confirmation'].sudo().search(
            [('access_token', '=', access_token)],
            limit=1)
        if not revised_quot_id:
            values['error'] = get_user_error('invalid_token')
            return request.render(template, values)
        values['revised_quot_id'] = revised_quot_id
        return request.render(template, values)

    # Consent
    @http.route(["/vehicle-service/consent-approval/",
                 "/vehicle-service/consent-approval/<string:access_token>"],
                type='http', auth="public", website=True)
    def user_consent_info(self, access_token=None, **kw):
        template = 'tk_vehicle_management.user_consent_details'
        inspection_obj = request.env['vehicle.inspection'].sudo()
        values = {}
        # Check Access Token
        if not access_token:
            values['error'] = get_user_error('not_access_token')
            return request.render(template, values)
        # Check Inspection Record
        inspection_id = inspection_obj.search([('consent_access_token', '=', access_token)],
                                              limit=1)
        if not inspection_id:
            values['error'] = get_user_error('consent_invalid_token')
            return request.render(template, values)
        values['inspection_id'] = inspection_id
        # Check Quotation Status
        if inspection_id.consent_sent_state in ['expire', 'reject', 'cancel']:
            error_type = None
            if inspection_id.consent_reopen_request in ['draft', False]:
                if inspection_id.consent_sent_state == 'expire':
                    error_type = 'consent_expired'
                elif inspection_id.consent_sent_state == 'reject':
                    error_type = 'consent_reject'
            else:
                error_type = 'consent_request_submit'
            values['error'] = get_user_error(error_type)
            return request.render(template, values)
        return request.render(template, values)

    # Consent Report
    @http.route('/vehicle-service/consent-report/<string:token>/Consent report', type='http',
                auth='public')
    def vehicle_concern_report_details(self, token):
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('consent_access_token', '=', token)], limit=1)
        if not inspection_id:
            return request.redirect('/')
        pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            "tk_vehicle_management.action_vehicle_inspection_concern_qweb_report", inspection_id.id)
        response = request.make_response(pdf_content, headers=[('Content-Type', 'application/pdf')])
        response.headers.add('Content-Disposition',
                             'inline; filename="%s"' % inspection_id.name + " ConsentReport.pdf")
        return response

    # Consent Approve
    @http.route(["/vehicle-service/user-consent/<string:access_token>/accept"], type='json',
                auth="public",
                website=True)
    def job_card_consent_accept(self, access_token=None, **kw):
        redirect_url = "/vehicle-service/consent-approval/%s" % access_token
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('consent_access_token', '=', access_token)])
        inspection_id.write({
            'customer_signature': kw.get('signature'),
            'consent_sent_state': 'signed',
            'consent_accept_date_time': fields.Datetime.now(),
            'status': 'concern_approve',
        })
        # Send Mail
        emails = [inspection_id.service_adviser_id.email,
                  inspection_id.sale_person_id.email]
        send_quotation_user_action_mail(values={
            'author_id': inspection_id.company_id.partner_id.id,
            'inspection_id': inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Consent Confirmed and Signed by Customer',
            'type': 'accepted',
            'for': 'consent',
            'reject_reason': None
        })
        return {
            'force_refresh': True,
            'redirect_url': redirect_url,
        }

    # Consent Reject
    @http.route('/vehicle-service/user-consent/consent-reject/reason', type='http', auth='public')
    def job_card_consent_reject(self, reject_reason=None, access_token=None, **kw):
        url = "/vehicle-service/consent-approval/%s" % access_token
        if not access_token:
            return request.redirect("/")
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('consent_access_token', '=', access_token)],
            limit=1)
        if reject_reason:
            inspection_id.write({
                'consent_reject_reason': reject_reason,
                'consent_sent_state': 'reject',
            })
        # Send Mail
        emails = [inspection_id.service_adviser_id.partner_id.email,
                  inspection_id.sale_person_id.partner_id.email]
        send_quotation_user_action_mail(values={
            'author_id': inspection_id.company_id.partner_id.id,
            'inspection_id': inspection_id.id,
            'email_to': ','.join(emails),
            'email_from': request.env.company.email,
            'subject': 'Consent Rejected by Customer',
            'type': 'rejected',
            'for': 'consent',
            'reject_reason': reject_reason
        })
        return request.redirect(url)

    @http.route(["/vehicle-service/user-consent/reopen-request/<string:access_token>"], type='http',
                auth="public",
                website=True)
    def user_consent_reopen_request(self, access_token=None, **kw):
        redirect_url = "/vehicle-service/consent-approval/%s" % access_token
        inspection_id = request.env['vehicle.inspection'].sudo().search(
            [('consent_access_token', '=', access_token)],
            limit=1)
        if inspection_id.consent_sent_state == 'expire':
            inspection_id.write({'consent_reopen_request': 'reopen_expire'})
        if inspection_id.consent_sent_state == 'reject':
            inspection_id.write({'consent_reopen_request': 'reopen_reject'})
        if inspection_id.consent_sent_state == 'cancel':
            inspection_id.write({'consent_reopen_request': 'reopen_cancel'})
        return request.redirect(redirect_url)

    @http.route("/register-vehicle", website=True, auth="user", type="http")
    def register_vehicle(self, **kw):
        """
            Register Vehicle
        """
        brands = request.env['fleet.vehicle.model.brand'].sudo().search([])
        values = {
            'brands': brands,
        }
        mandatory_fields = {
            "brand_id": "Brand",
            "vehicle_model_id": "Model",
            "year": "Year",
            "color": "Color",
            "vin_no": "VIN No.",
            "registration_no": "Registration No.",
            "fuel_type": "Fuel Type",
            "transmission": "Transmission",
        }
        if 'is_warranty' in kw:
            mandatory_fields.update({'warranty_type': 'Warranty Type'})
        error, request_data = validate_mandatory_fields(mandatory_fields, kw)
        if len(kw.get('vin_no')) != 17:
            error = "VIN No. should be 17 character long."
        if error:
            values['error'] = error
            kw.update(values)
            return request.render(
                'tk_vehicle_management.register_your_vehicle_form_web_template',
                kw)
        request_data['brand_id'] = int(kw.get('brand_id'))
        request_data['vehicle_model_id'] = int(kw.get('vehicle_model_id'))
        request_data['customer_id'] = request.env.user.partner_id.id
        if 'is_warranty' in kw and kw['is_warranty'] == 'on':
            request_data['is_warranty'] = True
        register_vehicle_id = request.env['register.vehicle'].sudo().create(request_data)
        url = f"/my/vehicle/registered-vehicle/form/{register_vehicle_id.access_token}"
        return request.redirect(url)

    @http.route("/my/register-vehicle-form", website=True, auth="user",
                type="http")
    def register_your_vehicle_form_view(self, **kw):
        """
        Register Vehicle Form Redirect
        """
        brands = request.env['fleet.vehicle.model.brand'].sudo().search([])
        values = {
            'brands': brands,
        }
        return request.render(
            'tk_vehicle_management.register_your_vehicle_form_web_template',
            values)


# Portal Details
class VehicleCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        inspection_obj = request.env['vehicle.inspection'].sudo()
        domain = [('customer_id', '=', request.env.user.partner_id.id)]
        job_card_ids = inspection_obj.search(domain).mapped('id')
        register_vehicle_obj = request.env['register.vehicle'].sudo()
        # Job Card
        job_card_count = inspection_obj.search_count(domain)
        values['job_card_count'] = job_card_count
        # Register Vehicle
        vehicle_count = register_vehicle_obj.search_count(domain)
        values['vehicle_count'] = vehicle_count
        # Register Vehicle Warranty
        warranty_count = request.env['vehicle.warranty'].sudo().search_count(domain)
        values['warrant_count'] = warranty_count
        # Quotation Count
        quot_count = inspection_obj.search_count(domain)
        values['quot_count'] = quot_count
        # Addition Part Quotation Count
        additional_part_quot_count = request.env[
            'additional.part.confirmation'].sudo().search_count(
            [('inspection_id', 'in', job_card_ids)])
        values['additional_part_quot_count'] = additional_part_quot_count
        return values

    def _prepare_portal_layout_values(self):
        # EXTEND 'portal'
        portal_layout_values = super()._prepare_portal_layout_values()
        portal_layout_values.update({
            'is_technician': request.env.user.is_technician,
        })
        return portal_layout_values
