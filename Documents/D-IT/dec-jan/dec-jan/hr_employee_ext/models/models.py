# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'Extended HR Employee'

    # inspection_vehicle_team_ids = fields.Many2many(
    # 'inspection.team',  
    # string="Teams"
    # )

    inspection_team_ids = fields.Many2many(
        'inspection.team', 'team_rel',
        'emp_id', 'team_id',
        string='Team')

    
    login = fields.Char(string="login")
    login_date = fields.Datetime(string='Latest authentication', readonly=False)
    team_leader = fields.Boolean(string="Team Leader")
    service_advisor = fields.Boolean(string="Service Advisor")
    receptionist = fields.Boolean(string="Receptionist")
    technician = fields.Boolean(string="Technician")





