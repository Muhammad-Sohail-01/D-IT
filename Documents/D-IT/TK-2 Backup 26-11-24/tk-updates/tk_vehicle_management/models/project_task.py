from odoo import api, fields, models, _
from markupsafe import Markup
from odoo.exceptions import UserError


STATUS_REF = {
    'not_started': 'tk_vehicle_management.evm_vehicle_project_stage_1',
    'in_progress': 'tk_vehicle_management.evm_vehicle_project_stage_2',
    'pending': 'tk_vehicle_management.evm_vehicle_project_stage_3',
    'waiting_parts': 'tk_vehicle_management.evm_vehicle_project_stage_4',
    'qc_check': 'tk_vehicle_management.evm_vehicle_project_stage_5',
    'qc_reject': 'tk_vehicle_management.evm_vehicle_project_stage_6',
    'complete': 'tk_vehicle_management.evm_vehicle_project_stage_7',
}


class VehicleRepairProject(models.Model):
    _inherit = 'project.project'


class VehicleInspectionTask(models.Model):
    _inherit = 'project.task'

    is_inspection_task = fields.Boolean()

    responsible_id = fields.Many2one('res.users', string="Responsible")
    health_report_id = fields.Many2one('vehicle.health.report', string="Health Report",
                                       ondelete='cascade')
    inspection_id = fields.Many2one('vehicle.inspection', string="Job Card", ondelete='cascade')
    status = fields.Selection(related="inspection_id.status")
    task_state = fields.Selection([('draft', 'Draft'),
                                   ('qc_check', 'QC Check'),
                                   ('complete', 'Complete'),
                                   ('reject', 'Reject')], default='draft')

    status_ref = fields.Char(compute="_compute_status_ref")

    # Team And Team Leaders
    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids",
                                        string="Team Leaders(technical)")
    # leaders_ids = fields.Many2many('res.users', string="Team Leaders",
    #                                domain="[('id','in',team_leaders_ids)]")

    leaders_ids = fields.Many2many('hr.employee', string="Team Leaders",
                                   domain="[('id','in',team_leaders_ids)]")

    # Parts & Service
    task_service_ids = fields.One2many('task.required.services', 'task_id', string="Task Service")
    task_parts_ids = fields.One2many('task.required.parts', 'task_id', string="Task Parts")

    # Additional Parts
    additional_parts_ids = fields.One2many("task.additional.parts", 'task_id',
                                           string="Additional Parts")

    # Service Adviser
    service_adviser_id = fields.Many2one(comodel_name='res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])

    task_type = fields.Selection([('qc_check', 'QC Check')])
    

    @api.depends('stage_id')
    def _compute_status_ref(self):
        """Get Status string fot task stage"""
        for rec in self:
            stage_external_id = rec.stage_id.get_external_id()
            status_ref = ""
            if stage_external_id:
                status_ref = next(key for key, value in STATUS_REF.items() if
                                  value == stage_external_id.get(rec.stage_id.id))
            rec.status_ref = status_ref

    # View Button
    def action_view_inspection(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inspection',
            'res_model': 'vehicle.inspection',
            'res_id': self.inspection_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_health_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Health Report',
            'res_model': 'vehicle.health.report',
            'res_id': self.health_report_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_request_qc_check(self):
        additional_part_check = False
        
        
            
        if self.is_timer_running or self.display_timer_resume:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Timer is running !'),
                    'message': _('Please stop timer to send for qc check.'),
                    'sticky': False,
                }}
        if self.additional_parts_ids:
            for part in self.additional_parts_ids:
                if part.status in ['pending_request', 'requested']:
                    additional_part_check = True
                    break
        if additional_part_check:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Additional Part Pending !'),
                    'message': _('Some additional part requests are pending or have been made.'),
                    'sticky': False,
                }}
        if self.status != 'parts_request' or self.status_ref != 'waiting_parts':
            raise UserError(_('Cannot proceed with QC Check! The job card must be in "Spare Parts" state to proceed with QC check.'))
        
        
        self.env['inspection.qc.check'].create({
            'task_id': self.id,
            'inspection_id': self.inspection_id.id
        })
        emails = self.leaders_ids.mapped('work_email')
        email_values = {
            'email_to': ','.join(emails),
            'email_from': self.env.company.sudo().email,
        }
        ctx = {
            'task_name': self.name,
            'jc_ref': self.inspection_id.name
        }
        template_id = self.env.ref('tk_vehicle_management.task_qc_check_mail_template').sudo()
        self.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(
            self.inspection_id.id, email_values=email_values, force_send=True)
        self.action_send_qc_whatsapp_message()
        self.task_state = 'qc_check'
        # Status : QC Check
        self._process_inspection_task_status(status_to='qc_check')

    def action_request_parts(self):
        required_parts = self.env['task.additional.parts'].search(
            [('task_id', '=', self.id), ('status', '=', 'pending_request')])
        if required_parts:
            emails = self.leaders_ids.mapped('login')
            emails.append(self.inspection_id.service_adviser_id.login)
            email_values = {
                'email_to': ','.join(emails),
                'email_from': self.env.company.sudo().email,
            }
            ctx = {
                'parts_details': required_parts,
            }
            template_id = self.env.ref(
                'tk_vehicle_management.task_requested_part_mail_template').sudo()
            self.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(
                self.inspection_id.id, email_values=email_values, force_send=True)
            self.inspection_id.update_quot_mail = True
            # Status : Waitint Parts
            self._process_inspection_task_status(status_to='waiting_parts')
        for data in self.additional_parts_ids:
            if data.status == 'pending_request':
                self.env['vehicle.required.parts'].create({
                    'product_id': data.product_id.id,
                    'name': data.name,
                    'qty': data.qty,
                    'price': data.product_id.lst_price,
                    'vehicle_health_report_id': self.inspection_id.vehicle_health_report_id.id,
                    'service_id': data.service_id.id,
                    'is_additional_part': True,
                    'inspection_id': self.inspection_id.id,
                    'additional_part_id': data.id,
                    'required_time': data.required_time
                })
                data.status = 'requested'

    def action_receive_requested_parts(self):
        """Receive Requested Parts"""
        is_any_pending_request = self.additional_parts_ids.filtered(
            lambda p: p.status in ['pending_request', 'requested'])
        if is_any_pending_request:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Additional Part Pending !'),
                    'message': _('Some additional part requests are pending or have been made.'),
                    'sticky': False,
                }}
        # Status : Pending
        self._process_inspection_task_status(status_to='pending')

    # Status: Complete
    def action_vehicle_task_complete(self, notify=None):
        self.task_state = 'complete'
        self._process_inspection_task_status(status_to='complete')
        if notify:
            body = Markup('<strong>Qc Check Passed</strong>')
            self.message_post(body=body, message_type="notification",
                              partner_ids=[self.env.user.partner_id.id])

    def action_complete_inspection_task(self):
        if self.is_timer_running or self.display_timer_resume:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Timer is running !'),
                    'message': _('Please stop timer to send complete task.'),
                    'sticky': False,
                }}
        active_users = self.check_active_timer_users(user_name=True)
        if active_users:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('The following user timers are running !'),
                    'message': active_users,
                    'sticky': False,
                }}
         # If task is for quality check, update the related job card to 'done'
        if self.task_type == 'qc_check':  # Assuming `task_type` or equivalent is the indicator
            job_card = self.env['vehicle.inspection'].search([
                ('task_ids', '=', self.id),  # Assuming `inspection_task_id` links the task to the job card
                ('status', '!=', 'qc_done')  # Ensure it's not already done
            ], limit=1)
            
            if job_card:
                job_card.write({'status': 'qc_done'})  # Mark the job card as done
    
        # Call the method to complete the vehicle task
        self.action_vehicle_task_complete()
        

    # Status : Qc Reject
    def action_vehicle_task_qc_reject(self, reject_reason):
        self.task_state = 'reject'
        html_body = Markup(
            f"<div class='text-danger'><strong>Qc Reject Reason</strong> : {reject_reason}</div>")
        self.message_post(body=html_body, message_type="comment",
                          subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'))
        self._process_inspection_task_status(status_to='qc_reject')

    # Change Status Timer
    def _process_inspection_task_status(self, status_to):
        """Update Task Status"""
        status_id = self.env.ref(STATUS_REF.get(status_to), raise_if_not_found=False)
        if status_id:
            self.stage_id = status_id.id

    # Status : In Progress
    def action_timer_start(self):
        super(VehicleInspectionTask, self).action_timer_start()
        if self.is_timer_running:
            self._process_inspection_task_status(status_to='in_progress')

    def action_timer_resume(self):
        super(VehicleInspectionTask, self).action_timer_resume()
        self._process_inspection_task_status(status_to='in_progress')

    # Status : Pending - Pause Timer, Stop Timer, Reset Draft
    def action_timer_pause(self):
        super(VehicleInspectionTask, self).action_timer_pause()
        active_users = self.check_active_timer_users(user_ids=True)
        if len(active_users) == 1:
            self._process_inspection_task_status(status_to='pending')

    def action_timer_stop(self):
        res = super(VehicleInspectionTask, self).action_timer_stop()
        active_users = self.check_active_timer_users(user_ids=True)
        if len(active_users) == 1:
            self._process_inspection_task_status(status_to='pending')
        return res

    def action_reset_draft(self):
        self.task_state = 'draft'
        self._process_inspection_task_status(status_to='pending')

    # Check users
    def check_active_timer_users(self, user_name=None, user_ids=None):
        """Check Active Timer Users"""
        user = None
        active_timer = self.env['timer.timer'].sudo().search([
            ('res_model', '=', 'project.task'),
            ('res_id', '=', self.id)
        ])
        if active_timer:
            active_users = active_timer.mapped('user_id')
            if user_name:
                user = ', '.join(active_users.mapped('name'))
            if user_ids:
                user = active_users.mapped('id')
        return user

    # Find WhatsApp Template
    def get_whatsapp_template(self, template_id):
        # Get Template from Settings
        wa_template_id = False
        config_template_id = self.env['ir.config_parameter'].sudo().get_param(template_id)
        if config_template_id:
            wa_template_id = self.env['whatsapp.template'].sudo().browse(int(config_template_id))
        return wa_template_id

    # Send WhatsApp Message
    def action_send_qc_whatsapp_message(self):
        wa_template_id = self.get_whatsapp_template(
            template_id='tk_vehicle_management.wa_team_leader_qc_template_id')
        if not wa_template_id:
            return
        for record in self.leaders_ids:
            mobile_no = self.check_whatsapp_phone(record.partner_id)
            if mobile_no:
                self.action_send_whatsapp_message(mobile_no, wa_template_id)

    # Check WhatsApp No
    def check_whatsapp_phone(self, partner_id):
        # Check WhatsApp Phone No
        mobile_no = False
        if partner_id.mobile:
            mobile_no = partner_id.mobile
        elif partner_id.phone:
            mobile_no = partner_id.phone
        return mobile_no

    # WhatsApp Send Message Action
    def _get_html_preview_whatsapp(self, wa_template_id, rec):
        # Prepare Body of whatsapp Message
        """This method is used to get the html preview of the whatsapp message."""
        self.ensure_one()
        # No of Text
        number_of_free_text = len(wa_template_id.variable_ids.filtered(
            lambda line: line.field_type == 'free_text' and line.line_type == 'body'))
        # Header Text
        header_text_1 = False
        if wa_template_id.header_type == 'text':
            header_params = wa_template_id.variable_ids.filtered(
                lambda line: line.line_type == 'header')
            if wa_template_id.variable_ids and header_params:
                header_param = header_params[0]
                if header_param.field_type == 'free_text' and not header_text_1:
                    header_text_1 = header_param.demo_value
        # Prepare Body
        template_variables_value = wa_template_id.variable_ids._get_variables_value(rec)
        text_vars = wa_template_id.variable_ids.filtered(lambda var: var.field_type == 'free_text')
        for var_index, body_text_var in zip(range(1, number_of_free_text + 1),
                                            text_vars.filtered(
                                                lambda var: var.line_type == 'body')):
            free_text_x = self[f'free_text_{var_index}']
            if free_text_x:
                template_variables_value[f'body-{body_text_var.name}'] = free_text_x
        if header_text_1 and text_vars.filtered(lambda var: var.line_type == 'header'):
            template_variables_value['header-{{1}}'] = self.header_text_1
        return wa_template_id._get_formatted_body(variable_values=template_variables_value)

    def action_send_whatsapp_message(self, phone, wa_template_id):
        # Send WhatsApp Message
        body = self._get_html_preview_whatsapp(wa_template_id, self)
        post_values = {'body': body,
                       'message_type': 'whatsapp_message',
                       'partner_ids': [self.env.user.partner_id.id], }
        message = self.env['mail.message'].create(
            dict(post_values, res_id=self.id, model=wa_template_id.model,
                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                     "mail.mt_note")))
        message = self.env['whatsapp.message'].sudo().create({
            'mobile_number': phone,
            'wa_template_id': wa_template_id.id,
            'wa_account_id': wa_template_id.wa_account_id.id,
            'mail_message_id': message.id,
        })
        message._send(force_send_by_cron=True)


class TaskRequiredServices(models.Model):
    _name = 'task.required.services'
    _description = 'Task Required Services'

    task_id = fields.Many2one('project.task', string="Task",
                              domain="[('detailed_type','=','service')]")
    product_id = fields.Many2one('product.product', string="Service")
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    estimate_time = fields.Float(string="Estimate Time")
    from_inspection = fields.Boolean()
    inspection_service_line_id = fields.Many2one('vehicle.required.services')

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.estimate_time = rec.product_id.estimate_time


class TaskRequiredParts(models.Model):
    _name = 'task.required.parts'
    _description = 'Task Required Parts'

    task_id = fields.Many2one('project.task', string="Task")
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    service_ids = fields.Many2many('task.required.services', compute="compute_services")
    service_id = fields.Many2one('task.required.services', string="Vehicle Service",
                                 domain="[('id','in',service_ids)]")
    inspection_part_line_id = fields.Many2one('vehicle.required.parts')
    inspection_service_line_id = fields.Many2one('vehicle.required.services')
    from_inspection = fields.Boolean()

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name

    @api.depends('task_id', 'task_id.task_service_ids')
    def compute_services(self):
        for rec in self:
            rec.service_ids = rec.task_id.task_service_ids.mapped('id')


class InspectionTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    service_ids = fields.Many2many('task.required.services', compute="compute_services",
                                   string="Services")
    service_id = fields.Many2one('task.required.services', string="Service",
                                 domain="[('id','in',service_ids)]")

    @api.depends('task_id', 'task_id.task_service_ids')
    def compute_services(self):
        for rec in self:
            rec.service_ids = rec.task_id.task_service_ids.mapped('id')


class TaskAdditionalParts(models.Model):
    _name = 'task.additional.parts'
    _description = 'Task Additional Parts'

    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    task_id = fields.Many2one('project.task', string="Task")
    service_ids = fields.Many2many('vehicle.required.services', compute="compute_services")
    service_id = fields.Many2one('vehicle.required.services', string="Vehicle Service",
                                 domain="[('id','in',service_ids)]")
    status = fields.Selection([('pending_request', 'Pending Request'),
                               ('requested', 'Requested'),
                               ('arrived', 'Arrived'),
                               ('reject', 'Rejected')], default="pending_request")
    required_time = fields.Float(string="Additional Required Time")

    @api.depends('task_id', 'task_id.task_service_ids')
    def compute_services(self):
        for rec in self:
            rec.service_ids = rec.task_id.task_service_ids.mapped(
                'inspection_service_line_id').mapped('id')

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name


class VehicleTimerTimer(models.Model):
    _inherit = 'timer.timer'

    def _get_float_time(self):
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        # timer was either running or paused
        if self.timer_pause:
            start_time += (stop_time - self.timer_pause)
        total_seconds = int((stop_time - start_time).total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
