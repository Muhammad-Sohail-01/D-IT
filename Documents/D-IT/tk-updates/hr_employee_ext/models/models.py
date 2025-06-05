# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'Extended HR Employee'

    inspection_team_ids = fields.Many2many(
        'inspection.team',
        string="Teams"
    )

    allowed_company_ids = fields.Many2many(
        'res.company',
        string="Allowed Companies",
        help="Companies that can see this product"
    )
    
    login = fields.Char(string="login")
    login_date = fields.Datetime(string='Latest authentication', readonly=False)
    team_leader = fields.Boolean(string="Team Leader")
    service_advisor = fields.Boolean(string="Service Advisor")
    receptionist = fields.Boolean(string="Receptionist")
    technician = fields.Boolean(string="Technician")





