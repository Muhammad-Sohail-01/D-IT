from odoo import api, fields, models


class AssignTeam(models.TransientModel):
    _name = 'assign.team'
    _description = 'Assign Team'

    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids", string="Team Leaders ")
    team_technician_ids = fields.Many2many(related="team_id.technician_ids",
                                           string="Team Technicians")
    leaders_ids = fields.Many2many('hr.employee', string="Team Leaders",
                                   domain="[('id','in',team_leaders_ids)]")
    technician_ids = fields.Many2many('hr.employee', 'assign_technician_rel',
                                      'assign_technician_id',
                                      'assign_user_technician_id',
                                      string="Technicians",
                                      domain="[('id','in',team_technician_ids),('technician','=',True)]")
    # Task Details
    task_title = fields.Char(string="Task Title")
    allocated_hours = fields.Float(string="Allotted Hours")
    tag_ids = fields.Many2many('project.tags', string="Tags")

    # Inspection Type
    inspection_type_id = fields.Many2one('inspection.type', string="Inspection Type")

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(AssignTeam, self).default_get(fields)
        active_id = self._context.get('active_id')
        inspection_id = self.env['vehicle.inspection'].browse(active_id)
        res['task_title'] = str(inspection_id.name) + " 's Task"
        return res

    @api.onchange('inspection_type_id')
    def _onchange_inspection_type_id(self):
        for record in self:
            if record.inspection_type_id:
                record.allocated_hours = record.inspection_type_id.hours

    def action_assign_team(self):
        active_id = self._context.get('active_id')
        inspection_id = self.env['vehicle.inspection'].browse(active_id)
        health_report_id = inspection_id.vehicle_health_report_id
        if not health_report_id:
            health_report_id = self.env['vehicle.health.report'].create({
                'inspection_id': inspection_id.id,
                'team_id': self.team_id.id,
                'leaders_ids': [(6, 0, self.leaders_ids.ids)],
                'technician_ids': [(6, 0, self.technician_ids.ids)],
                'inspection_type_id': self.inspection_type_id.id
            })
            inspection_id.vehicle_health_report_id = health_report_id.id
        if health_report_id:
            health_report_id.write({
                'team_id': self.team_id.id,
                'leaders_ids': [(6, 0, self.leaders_ids.ids)],
                'technician_ids': [(6, 0, self.technician_ids.ids)],
                'inspection_type_id': self.inspection_type_id.id
            })
        for data in inspection_id.inner_image_ids:
            name = '[Inner Body] ' + str(data.name)
            self.env['inspection.images'].create(
                {'name': name,
                 'avatar': data.avatar,
                 'inspection_id': health_report_id.id}
            )
        for data in inspection_id.outer_image_ids:
            name = '[Outer Body] ' + str(data.name)
            self.env['inspection.images'].create(
                {'name': name,
                 'avatar': data.avatar,
                 'inspection_id': health_report_id.id}
            )
        for data in inspection_id.other_image_ids:
            name = '[Other] ' + str(data.name)
            self.env['inspection.images'].create(
                {'name': name,
                 'avatar': data.avatar,
                 'inspection_id': health_report_id.id}
            )
        task_id = self.env['project.task'].sudo().create({
            'name': self.task_title,
            'allocated_hours': self.allocated_hours,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'project_id': self.env.ref('tk_vehicle_management.evm_vehicle_project').id,
            'partner_id': inspection_id.customer_id.id,
            'responsible_id': self.env.user.id,
            'user_ids': [(6, 0, self.technician_ids.ids)],
            'health_report_id': inspection_id.vehicle_health_report_id.id,
            'team_id': self.team_id.id,
            'leaders_ids': [(6, 0, self.leaders_ids.ids)],
            'inspection_id': inspection_id.id,
            'is_inspection_task': True,
            'service_adviser_id': inspection_id.service_adviser_id.id,
        })
        inspection_id.vehicle_health_report_id.task_id = task_id.id
        inspection_id.is_inspection_created = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Inspection',
            'res_model': 'vehicle.health.report',
            'res_id': inspection_id.vehicle_health_report_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }
