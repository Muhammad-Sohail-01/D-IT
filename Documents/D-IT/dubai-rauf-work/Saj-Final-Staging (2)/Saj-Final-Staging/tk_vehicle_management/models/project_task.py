from odoo import api, fields, models, _


class VehicleInspectionTask(models.Model):
    _inherit = 'project.task'

    is_inspection_task = fields.Boolean()

    responsible_id = fields.Many2one('res.users', string="Responsible")
    health_report_id = fields.Many2one('vehicle.health.report', string="Health Report", ondelete='cascade')
    inspection_id = fields.Many2one('vehicle.inspection', string="Job Card", ondelete='cascade')
    task_state = fields.Selection([('draft', 'Draft'), ('qc_check', 'QC Check'), ('complete', 'Complete'),
                                   ('reject', 'Reject')], default='draft')

    # Team And Team Leaders
    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids", string="Team Leaders(technical)")
    leaders_ids = fields.Many2many('res.users', string="Team Leaders", domain="[('id','in',team_leaders_ids)]")

    # Parts & Service
    task_service_ids = fields.One2many('task.required.services', 'task_id', string="Task Service")
    task_parts_ids = fields.One2many('task.required.parts', 'task_id', string="Task Parts")

    # Additional Parts
    additional_parts_ids = fields.One2many("task.additional.parts", 'task_id', string="Additional Parts")

    # Service Adviser
    service_adviser_id = fields.Many2one(comodel_name='res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])

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
        self.env['inspection.qc.check'].create({
            'task_id': self.id,
            'inspection_id': self.inspection_id.id
        })
        emails = self.leaders_ids.mapped('login')
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

    def action_reset_draft(self):
        self.task_state = 'draft'

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
            template_id = self.env.ref('tk_vehicle_management.task_requested_part_mail_template').sudo()
            self.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(
                self.inspection_id.id, email_values=email_values, force_send=True)
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
                    'additional_part_id': data.id,
                    'required_time': data.required_time
                })
                data.status = 'requested'

        self.inspection_id.update_quot_mail = True

    # Find WhatsApp Template
    def get_whatsapp_template(self, template_id):
        # Get Template from Settings
        wa_template_id = False
        config_template_id = self.env['ir.config_parameter'].sudo().get_param(template_id)
        if config_template_id:
            wa_template_id = self.env['whatsapp.template'].sudo().browse(int(config_template_id))
        return wa_template_id

    # Send Whatsapp Message
    def action_send_qc_whatsapp_message(self):
        wa_template_id = self.get_whatsapp_template(template_id='tk_vehicle_management.wa_team_leader_qc_template_id')
        if not wa_template_id:
            return
        for record in self.leaders_ids:
            mobile_no = self.check_whatsapp_phone(record.partner_id)
            if mobile_no:
                self.action_send_whatsapp_message(mobile_no, wa_template_id)

    # Check Whatsapp No
    def check_whatsapp_phone(self, partner_id):
        # Check WhatsApp Phone No
        mobile_no = False
        if partner_id.mobile:
            mobile_no = partner_id.mobile
        elif partner_id.phone:
            mobile_no = partner_id.phone
        return mobile_no

    # Whatsapp Send Message Action
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

    def action_send_whatsapp_message(self, phone, wa_template_id):
        # Send Whatsapp Message
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


class TaskRequiredServices(models.Model):
    _name = 'task.required.services'
    _description = 'Task Required Services'

    task_id = fields.Many2one('project.task', string="Task", domain="[('detailed_type','=','service')]")
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
    product_id = fields.Many2one('product.product', string="Part", domain="[('detailed_type','=','product')]")
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    service_ids = fields.Many2many('task.required.services', compute="compute_services")
    service_id = fields.Many2one('task.required.services', string="Vehicle Service", domain="[('id','in',service_ids)]")
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

    service_ids = fields.Many2many('task.required.services', compute="compute_services", string="Services")
    service_id = fields.Many2one('task.required.services', string="Service", domain="[('id','in',service_ids)]")

    @api.depends('task_id', 'task_id.task_service_ids')
    def compute_services(self):
        for rec in self:
            rec.service_ids = rec.task_id.task_service_ids.mapped('id')


class TaskAdditionalParts(models.Model):
    _name = 'task.additional.parts'
    _description = 'Task Additional Parts'

    product_id = fields.Many2one('product.product', string="Part", domain="[('detailed_type','=','product')]")
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
            rec.service_ids = rec.task_id.task_service_ids.mapped('inspection_service_line_id').mapped('id')

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name
