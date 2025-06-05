from odoo import fields, api, models


class TaskAssign(models.TransientModel):
    _name = 'task.assignation'
    _description = "Task Assignation"
    _rec_name = 'task_title'

    # Inspection Details
    inspection_id = fields.Many2one('vehicle.inspection', string="Vehicle Inspection")
    health_report_id = fields.Many2one(related="inspection_id.vehicle_health_report_id")
    service_ids = fields.Many2many('vehicle.required.services', string="Services")

    # Task Details
    task_title = fields.Char(string="Task Title")
    allocated_hours = fields.Float(string="Allotted Hours", compute="compute_hours")
    tag_ids = fields.Many2many('project.tags', string="Tags")

    # Team
    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids", string="Team Leaders List")
    team_technician_ids = fields.Many2many(related="team_id.technician_ids", string="Team Technicians")
    leaders_ids = fields.Many2many('res.users', string="Team Leaders",
                                   domain="[('id','in',team_leaders_ids),('employee_id','!=',False)]")
    technician_ids = fields.Many2many('res.users', 'task_assign_technician_rel', 'task_assign_technician_id',
                                      'task_assign_user_technician_id', string="Technicians",
                                      domain="[('id','in',team_technician_ids),('employee_id','!=',False)]")

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(TaskAssign, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['inspection_id'] = active_id
        return res

    @api.depends('service_ids')
    def compute_hours(self):
        for rec in self:
            rec.allocated_hours = sum(rec.service_ids.mapped('estimate_time'))

    def action_assign_service_task(self):
        task_id = self.env['project.task'].create({
            'name': self.task_title,
            'allocated_hours': self.allocated_hours,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'project_id': self.env.ref('tk_vehicle_management.evm_vehicle_project').id,
            'partner_id': self.inspection_id.customer_id.id,
            'responsible_id': self.env.user.id,
            'inspection_id': self.inspection_id.id,
            'team_id': self.team_id.id,
            'leaders_ids': [(6, 0, self.leaders_ids.ids)],
            'user_ids': [(6, 0, self.technician_ids.ids)],
            'service_adviser_id': self.inspection_id.service_adviser_id.id,
        })
        for data in self.service_ids:
            self.env['task.required.services'].create({
                'task_id': task_id.id,
                'product_id': data.product_id.id,
                'name': data.name,
                'qty': data.qty,
                'estimate_time': data.estimate_time,
                'from_inspection': True,
                'inspection_service_line_id': data.id
            })
            data.task_id = task_id.id
        for data in task_id.task_service_ids:
            for product in self.inspection_id.inspection_required_parts_ids:
                if data.inspection_service_line_id.id == product.service_id.id:
                    self.env['task.required.parts'].create({
                        'task_id': task_id.id,
                        'product_id': product.product_id.id,
                        'name': product.name,
                        'qty': product.qty,
                        'service_id': data.id,
                        'inspection_part_line_id': product.id,
                        'inspection_service_line_id': data.inspection_service_line_id.id,
                        'from_inspection': True
                    })

        self.inspection_id.status = 'in_repair'
