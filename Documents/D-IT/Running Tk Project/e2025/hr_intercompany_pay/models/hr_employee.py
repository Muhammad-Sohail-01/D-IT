# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    cost_input = fields.Float(string="Cost Input")
    job_accepted_date = fields.Date(string="Job Accepted Date")
