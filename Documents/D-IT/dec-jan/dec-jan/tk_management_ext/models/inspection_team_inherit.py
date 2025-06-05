from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InspectionTeamInherit(models.Model):
    _inherit = 'inspection.team'
    _description = 'inspection team inherit for updates'

    # hr_team_leader_ids = fields.Many2many('hr.employee', string="Team Leaders",
    #                                 )
    # hr_technician_ids = fields.Many2many('hr.employee', 'hr_team_technician_rel', 'hr_technician_id',
    #                                   'hr_technician_employee_id',
    #                                   )

    team_leader_ids = fields.Many2many('hr.employee', string="Team Leaders" ,
                                       domain=[('team_leader', '=', True)]
                                       )
    technician_ids = fields.Many2many('hr.employee', 'team_technician_rel', 'technician_id',
                                      'technician_user_id',
                                      string='Technicians',
                                      domain=[('technician', '=', True)]
                                      )
