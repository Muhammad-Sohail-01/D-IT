# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError



class HRContract(models.Model):
    _inherit = 'hr.contract'

    total_salary_month = fields.Float (
        string='Total Monthly Salary',
        compute='_compute_total_salary_month',
        store=True,
        help='Total monthly salary including basic wage and all allowances'
    )

    @api.depends('wage', 'l10n_ae_housing_allowance', 'l10n_ae_other_allowances', 'l10n_ae_transportation_allowance')
    def _compute_total_salary_month(self):
        for contract in self:
            contract.total_salary_month = sum([
                contract.wage or 0.0,
                contract.l10n_ae_housing_allowance or 0.0,
                contract.l10n_ae_other_allowances or 0.0,
                contract.l10n_ae_transportation_allowance or 0.0
            ])

    @api.model
    def _update_l10n_ae_number_of_days(self):
        today = fields.Date.today ()
        employees = self.env['hr.contract'].search ([])

        for contract in employees:
            employee = contract.employee_id
            if employee.job_accepted_date:
                job_accepted_date = fields.Date.from_string (employee.job_accepted_date)
                employment_duration = (today - job_accepted_date).days
                

                if employment_duration <= 5 * 365:  # 5 years or less
                    contract.l10n_ae_number_of_days = 21
                    
                else:
                    contract.l10n_ae_number_of_days = 30

