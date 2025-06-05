from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResEmployee(models.Model):
    _inherit = 'hr.payslip'

    affiliation_company_ids = fields.One2many('hr.payslip.affiliation.line', 'affiliation_id')