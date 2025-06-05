from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class TimeOffController(http.Controller):

    @http.route('/time-off/form', auth='user', website=True, methods=['GET', 'POST'])
    def time_off_form(self, **post):
        values = {}
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not employee:
            _logger.info("No employee found for user ID: %s", request.env.user.id)
            return request.redirect('/my/home')

        if post:
            # Convert date strings to date objects
            try:
                start_date = datetime.strptime(post.get('request_date_from'), DATE_FORMAT).date()
                end_date = datetime.strptime(post.get('request_date_to'), DATE_FORMAT).date()
            except Exception as e:
                values['error_message'] = "Invalid date format. Please ensure the dates are correctly entered."
                _logger.exception("Date conversion error: %s", e)
                return request.render('time_off_portal.time_off_form_page', values)

            try:
                time_off_data = {
                    'holiday_status_id': int(post.get('holiday_status_id')),
                    'request_date_from': start_date,
                    'request_date_to': end_date,
                    'name': post.get('description'),
                    'employee_id': employee.id,
                }
                request.env['hr.leave'].sudo().create(time_off_data)
                return request.redirect('/time-off/listing')
            except ValidationError as e:
                # Prepare the error message and other necessary template data
                values['error_message'] = "Your selected dates overlap with an existing time-off request. Please choose a different period."
                values['leave_types'] = request.env['hr.leave.type'].sudo().search([])  # Re-fetch leave types in case of error
                
                # Ensure consistent context/environment when re-rendering the template
                return request.render('time_off_portal.time_off_form_page', values, context=request.context)
        else:
            values['leave_types'] = request.env['hr.leave.type'].sudo().search([])
        
        return request.render('time_off_portal.time_off_form_page', values)

    @http.route('/time-off/listing', auth='user', website=True)
    def time_off_listing(self):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not employee:
            _logger.info("No employee found for user ID: %s", request.env.user.id)
            return request.render('time_off_portal.time_off_listing_page', {'time_off_requests': []})

        domain = [('employee_id', '=', employee.id)]
        time_off_requests = request.env['hr.leave'].sudo().search(domain)
        return request.render('time_off_portal.time_off_listing_page', {'time_off_requests': time_off_requests})

    @http.route('/time-off/details/<int:time_off_id>', auth='user', website=True)
    def time_off_details(self, time_off_id):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not employee:
            _logger.info("Attempt to access time-off details without a valid employee record for user ID: %s", request.env.user.id)
            return request.redirect('/time-off/listing')

        time_off_request = request.env['hr.leave'].sudo().browse(time_off_id)
        if not time_off_request.exists() or (time_off_request.employee_id != employee and not request.env.user.has_group('hr_holidays.group_hr_holidays_manager')):
            _logger.info("Unauthorized access attempt or invalid time-off ID: %s by user ID: %s", time_off_id, request.env.user.id)
            return request.redirect('/time-off/listing')

        return request.render('time_off_portal.time_off_details_page', {'time_off_request': time_off_request})
