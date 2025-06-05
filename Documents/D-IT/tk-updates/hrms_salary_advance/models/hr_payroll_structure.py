# -*- coding: utf-8 -*-

from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    max_percent = fields.Integer(string='Max.Salary Advance Percentage',
                                 help="Maximum salary advance percentage")
    advance_date = fields.Integer(string='Salary Advance-After days',
                                  help="Salary advance after days")
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
