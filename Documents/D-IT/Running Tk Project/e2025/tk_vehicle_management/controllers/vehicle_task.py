import base64
import logging
from markupsafe import Markup

from odoo import fields, SUPERUSER_ID, api
from odoo.addons.test_convert.tests.test_env import record
from odoo.http import request, route
from odoo import http, tools, _
from odoo.service.server import start

_logger = logging.getLogger(__name__)

MODEL_DICT = {
    # Inspection Type
    'interior': 'vehicle.interior.condition',
    'exterior': 'vehicle.outer.condition',
    'under_hood': 'mechanical.condition.line',
    'fluid': 'vehicle.fluids.line',
    'tyre': 'tyre.inspection.line',
    'u_vehicle': 'under.vehicle.inspection.line',
    'brake': 'brake.condition.line',
    'multi_point': 'vehicle.components.line',
    # Part Model
    'unlink_interior': 'inner.condition.parts',
    'unlink_exterior': 'outer.condition.parts',
    'unlink_under_hood': 'mechanical.condition.parts',
    'unlink_fluid': 'fluid.condition.parts',
    'unlink_tyre': 'tyre.condition.parts',
    'unlink_u_vehicle': 'under.vehicle.parts',
    'unlink_brake': 'brake.condition.parts',
    'unlink_multi_point': 'components.condition.parts',
    # Image Model
    'image_interior': 'interior.images',
    'image_exterior': 'exterior.images',
    'image_under_hood': 'under.hood.images',
    'image_fluid': 'fluid.images',
    'image_tyre': 'tyre.images',
    'image_u_vehicle': 'under.vehicle.images',
    'image_brake': 'brake.images',
    'image_multi_point': 'multipoint.images',
}


def handle_model_info(model):
    """Check Model name based on the given 'model'."""
    model_info = MODEL_DICT.get(model)
    if model_info is not None:
        return model_info
    _logger.warning("Model '%s' not found in registry.", model)
    return None


def validate_record_existence(access_token, model):
    """Check whether the record is available for the given model."""
    res_model = handle_model_info(model)

    if not access_token:
        _logger.warning("Resource ID is missing.")
        return None

    if not res_model:
        _logger.warning("No valid model found for '%s'.", model)
        return None

    record = request.env[res_model].sudo().search([('access_token', '=', access_token)], limit=1)
    if not record.exists():
        _logger.warning("Record with ID '%s' in model '%s' not found.", access_token, res_model)
        return None

    return record  # Return the record object


def invalid_record_response(url):
    """Invalid Record Response"""
    return {
        'status': False,
        'url': url
    }


def time_str_to_float(time_str):
    if not time_str:
        return 0
    hours, minutes = map(int, time_str.split(':'))
    # Convert to float: hours + (minutes / 60)
    return hours + minutes / 60.0


class VehicleTecnicinaTask(http.Controller):
    @http.route(["/my/tasks/<string:action>/<int:task_id>"],
                type='http',
                auth="user", website=True)
    def vehicle_task_timer_start(self, action, task_id, **kw):
        if not task_id or not isinstance(task_id, int):
            return request.redirect("/my")
        task = request.env['project.task'].with_user(request.env.user.id).sudo().browse(
            int(task_id))
        if action == "start-timer":
            task.action_timer_start()
        if action == "stop-timer":
            rounded_hours = task._get_rounded_hours(task.user_timer_id._get_minutes_spent())
            request.env['account.analytic.line'].sudo().create({
                'task_id': task.id,
                'project_id': task.project_id.id,
                'date': fields.Datetime.today(),
                'name': kw.get('activity') if kw.get('activity') else '/',
                'user_id': request.env.user.id,
                'unit_amount': rounded_hours,
                'service_id': kw.get('service_id') if kw.get('service_id') else False,
            })
            task.action_timer_stop()
            task.user_timer_id.unlink()
        if action == "pause-timer":
            task.action_timer_pause()
        if action == "resume-timer":
            task.action_timer_resume()
        if action == "clear-timer":
            existing_timer_rec = request.env['timer.timer'].sudo().search(
                [('user_id', '=', request.env.user.id), ('res_model', '=', 'project.task'),
                 ('res_id', '=', task.id)])
            if existing_timer_rec:
                existing_timer_rec.unlink()
        return request.redirect(f"/my/tasks/{task_id}")

    @http.route(["/my/tasks/portal-inspection/<string:action>"],
                type='http',
                auth="user", website=True)
    def vehicle_portal_inspection(self, action):
        """Portal Inspection Boolean Selection"""
        res_id, type, inspection = action.split('-')
        record_id = validate_record_existence(access_token=res_id, model=inspection)
        if not record_id:
            return request.redirect("/my")
        task_id = record_id.inspection_id.task_id.id
        self._process_boolean_selection(type, record_id)
        return request.redirect(f"/my/tasks/{task_id}#{inspection}-flush-{res_id}")

    def _process_boolean_selection(self, type, record_id):
        """Process Inspection Requirement"""
        boolean_fields = ['required_attention', 'further_attention', 'okay_for_now']

        if type in boolean_fields:
            values = {field: field == type for field in boolean_fields}
            record_id.write(values)

    @http.route('/add/parts-services', type='json', auth="user")
    def add_service_part(self, data):
        """Add type wise product"""
        new_part_id = None
        # Check Record
        record_id = validate_record_existence(access_token=data.get('id'),
                                              model=data.get('type'))
        if not record_id:
            return invalid_record_response(url="/")
        # Prepare Service Data
        service_id = int(data['service_id']) if data['service_id'] else False

        # Prepare Part Data
        part_id = int(data['part_id']) if data['part_id'] else False
        product_qty = float(data['product_qty']) if data['product_qty'] else 0.0

        # Add Services
        if service_id and service_id not in record_id.service_ids.ids:
            updated_service_ids = record_id.service_ids.ids + [service_id]
            record_id.service_ids = [(6, 0, updated_service_ids)]

        # Add Parts
        if part_id and product_qty > 0:
            part_model = f"unlink_{data['type']}"
            new_part_id = request.env[MODEL_DICT.get(part_model)].sudo().create({
                'product_id': part_id,
                'qty': product_qty,
                'service_id': service_id or False,
                'condition_id': record_id.id,
            })
        part_id = request.env['product.product'].sudo().browse(part_id)
        part_line_id = f"unlink_{data['type']}-{new_part_id.id}-part-unlink-line" if new_part_id else None
        part_unlink_id = f"unlink_{data['type']}-{new_part_id.id}-part-unlink" if new_part_id else None
        return {
            'status': True,
            'service_name': request.env['product.product'].sudo().browse(service_id).name,
            'service_id': f"{data['type']}-{data['id']}-{service_id}-service-unlink",
            'part_name': part_id.name if part_id else "",
            'product_qty': str(float(product_qty)) if product_qty > 0 else "",
            'product_unit': part_id.uom_id.name if part_id else "",
            'part_line_id': part_line_id,
            'part_unlink_id': part_unlink_id
        }

    @http.route('/unlink/part-line', type='json', auth="user")
    def unlink_service_part_line(self, data):
        """Unlike Part line as per type"""
        res_model = handle_model_info(data['type'])
        if not res_model:
            return invalid_record_response(url="/")
        record_id = request.env[res_model].sudo().browse(
            int(data['part_line_id'])).exists()
        if not record_id:
            return invalid_record_response(url="/")
        record_id.unlink()
        return {
            'status': True,
        }

    @http.route('/unlink/services', type='json', auth="user")
    def unlink_service_line(self, data):
        """Unlink Part line as per type"""

        # Check Record
        record_id = validate_record_existence(access_token=data['record_id'],
                                              model=data['type'])
        if not record_id:
            return invalid_record_response(url="/")

        # Early exit if service_id is not provided or is already linked with parts
        service_id = data.get('service_id')
        if not service_id or int(service_id) in set(record_id.part_ids.mapped('service_id.id')):
            service_name = request.env['product.product'].sudo().browse(int(service_id)).name
            return {
                'service_name': service_name,
                'status': True
            }

        # Update service_ids by removing the specified service_id
        service_id = int(service_id)
        updated_service_ids = set(record_id.service_ids.ids)  # Using a set for efficient removal
        updated_service_ids.discard(service_id)  # discard is safe if service_id is not in the set
        record_id.service_ids = [(6, 0, list(updated_service_ids))]
        return {
            'status': True
        }

    @http.route('/inspection/details/video-note', type='json', auth="user")
    def add_service_note_details(self, data):
        """Update service note or inspection video based on type."""

        # Check Record
        record_id = validate_record_existence(access_token=data['record_id'],
                                              model=data['type'])
        if not record_id:
            return invalid_record_response(url="/")

        # Update Note
        if record_id.notes != data.get('data'):
            record_id.write({'notes': data['data']})

        return {
            'status': True,
        }

    @http.route(["/upload-inspection-video/<string:type>/<string:access_token>/i_video"],
                type='http',
                auth="user", website=True)
    def vehicle_add_inspection_video(self, type, access_token, **kw):
        """Vehicle Inspection Video"""

        # Check Record
        record_id = validate_record_existence(access_token=access_token,
                                              model=type)
        if not record_id:
            return invalid_record_response(url="/")

        task_id = record_id.inspection_id.task_id.id
        file_data = kw.get('inspection_video')
        file_name = file_data.filename
        if file_data and file_name:
            record_id.write({
                'inspection_video': base64.b64encode(file_data.read()),
                'file_name': file_name,
            })
        return request.redirect(f"/my/tasks/{task_id}#{type}-flush-{access_token}")

    @http.route('/inspection/details/add-image', type='json', auth="user")
    def portal_inspection_add_image(self, data):
        """Add images of inspection"""
        model_name = f"image_{data['type']}"

        # Check Model
        model = handle_model_info(model=model_name)
        if not model:
            return invalid_record_response(url="/")

        # Check Record
        record_id = validate_record_existence(access_token=data.get('record_id'),
                                              model=data.get('type'))
        if not record_id:
            return invalid_record_response(url="/")
        input_image = data.get('image').split(',')[1]
        image_id = request.env[model].sudo().create({
            'name': data.get('image_title') if data.get('image_title') else "Image",
            'avtar': input_image.encode('utf-8'),
            'inspection_id': record_id.id,
        })
        return {
            'image_id': image_id.id,
            'status': True,
        }

    @http.route('/inspection/details/image-unlink', type='json', auth="user")
    def portal_inspection_image_unlink(self, data):
        """inspection image unlink"""
        model_name = f"image_{data['type']}"
        # Check Modal
        model = handle_model_info(model=model_name)
        if not model:
            return invalid_record_response(url="/")
        record_id = request.env[model].sudo().browse(int(data['record_id']))
        # Check Record
        if not record_id:
            return invalid_record_response(url="/")
        # Unlink Record
        record_id.unlink()
        return {
            'status': True,
        }

    @http.route('/inspection/details/tyre-info', type='json', auth="user")
    def portal_inspection_tyre_info(self, data):
        """inspection tyre details"""
        record_id = validate_record_existence(access_token=data.get('record_id'),
                                              model=data['type'])
        if not record_id:
            return invalid_record_response(url="/")
        record_id.write(data.get('tyre_info', {}))
        return {
            'status': True,
        }

    @http.route(["/task/inspection/submit/<int:health_report_id>"],
                type='http',
                auth="user", website=True)
    def vehicle_portal_inspection_complete(self, health_report_id):
        """Health Report Inspection"""
        record_id = request.env['vehicle.health.report'].sudo().browse(int(health_report_id))
        redirect_url = "/"
        if record_id:
            redirect_url = f"/my/tasks/{record_id.task_id.id}"
            record_id.task_id.action_vehicle_task_complete()
            record_id.write({
                'status': 'complete'
            })
            record_id.action_add_service_parts()
        return request.redirect(redirect_url)

    @http.route(['/inspection/check-timer-users/'], type='json', auth="user")
    def check_task_timer_users(self, data):
        """Check Task Timer Users"""
        health_report_id = request.env['vehicle.health.report'].sudo().browse(
            int(data['health_report_id']))
        if not health_report_id:
            return invalid_record_response(url="/")
        task_users = health_report_id.task_id.check_active_timer_users(user_name=True)
        if task_users:
            return {
                'status': True,
                'users': task_users,
            }
        return {
            'status': True,
            'url': '/task/inspection/submit/' + str(health_report_id.id),
        }

    @http.route(['/inspection/qc-check/request'], type='json', auth="user")
    def inspection_quality_check_request(self, data):
        """Inspection Quality Check Request"""
        try:
            task_id = request.env['project.task'].sudo().browse(int(data['task_id']))
        except (ValueError, TypeError):
            return {
                'status': False,
                'url': '/',
            }
        if not task_id:
            return invalid_record_response(url="/")

        # Check for active timer
        if task_id.is_timer_running or task_id.display_timer_resume:
            return {
                'status': False,
                'error': 'Please stop timer to send for qc check.',
            }

        # Check for pending or requested additional parts
        additional_part_check = any(
            part.status in ['pending_request', 'requested']
            for part in task_id.additional_parts_ids
        )

        if additional_part_check:
            return {
                'status': False,
                'error': 'Some additional part requests are pending or have been made. Please wait until all requests are completed',
            }

        # If all checks pass, proceed with QC request
        task_id.action_complete_inspection_task()
        return {
            'status': True,
        }

    @http.route(["/task/reset-qc-check/<int:task_id>"],
                type='http',
                auth="user", website=True)
    def task_qc_reset(self, task_id):
        """Inspection Task Quality Check Reset"""
        try:
            task_record_id = request.env['project.task'].sudo().browse(int(task_id))
        except (ValueError, TypeError):
            return request.redirect("/")
        if not task_record_id:
            return request.redirect("/")
        # Change Status to Draft
        task_record_id.action_reset_draft()
        return request.redirect(f"/my/tasks/{task_record_id.id}")

    @http.route('/add/addition-part', type='json', auth="user")
    def add_additional_part(self, data):
        """Add Additional Part"""
        # Check Access Token
        if not data.get('access_token'):
            return invalid_record_response(url="/")
        task_id = request.env['project.task'].sudo().search(
            [('access_token', '=', data.get('access_token'))], limit=1)
        if not task_id:
            return invalid_record_response(url="/")
        product_id = request.env['product.product'].sudo().browse(int(data['part_id']))
        additional_part_id = request.env['task.additional.parts'].sudo().create({
            'task_id': task_id.id,
            'product_id': product_id.id,
            'name': product_id.name,
            'qty': float(data['part_qty']),
            'service_id': int(data['service_id']),
            'required_time': time_str_to_float(data.get('additional_time')),
        })
        return {
            'status': True,
            'part_name': str(product_id.name),
            'service_name': additional_part_id.service_id.name,
            'qty': data['part_qty'],
            'required_time': data.get('additional_time'),
            'unit': product_id.uom_id.name,
            'additional_part_line_id': additional_part_id.id,
            'tr_line_id': f"{task_id.access_token}-{additional_part_id.id}-tr-additional",
        }

    @http.route('/unlink/additional-part-line', type='json', auth="user")
    def unlink_additional_part_line(self, data):
        """Unlink Additional Part Line"""
        try:
            part_line_id = request.env['task.additional.parts'].sudo().browse(
                int(data['part_line_id']))
        except (ValueError, TypeError):
            return {
                'status': False,
                'url': '/',
            }
        if not part_line_id:
            return invalid_record_response(url="/")
        access_token = part_line_id.task_id.access_token
        additional_part_line_id = part_line_id.id
        part_line_id.unlink()
        return {
            'status': True,
            'tr_line_id': f"{access_token}-{additional_part_line_id}-tr-additional",
        }

    @http.route('/request/pending/additional-part', type='json', auth="user")
    def request_pending_additional_part(self, data):
        """Check Task Record"""
        if not data.get('access_token'):
            return invalid_record_response(url="/")
        task_id = request.env['project.task'].sudo().search(
            [('access_token', '=', data.get('access_token'))], limit=1)
        if not task_id:
            return invalid_record_response(url="/")
        pending_additional_part = task_id.additional_parts_ids.filtered(
            lambda p: p.status == 'pending_request')
        if not pending_additional_part:
            return {
                'status': True,
                'error': 'No pending parts. Please add to requested parts'
            }

        task_id.action_request_parts()
        return {
            'status': True,
            'error': False,
            'url': f"/my/tasks/{task_id.id}"
        }
