# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    salary_distribution_ids = fields.One2many(
        'hr.salary.distribution', 'payslip_id', string="Salary Distributions"
    )

    def action_create_journal_entry(self):
        """Create a journal entry for salary distribution."""
        for payslip in self:
            if not payslip.salary_distribution_ids:
                raise ValueError("No salary distribution lines found.")

            move_vals = {
                'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
                'line_ids': [],
            }
            for line in payslip.salary_distribution_ids:
                move_vals['line_ids'].append((0, 0, {
                    'account_id': self.env['account.account'].search([
                        ('company_id', '=', line.company_id.id),
                        ('code', 'ilike', 'Salary Expense')
                    ], limit=1).id,
                    'debit': line.salary_portion,
                    'credit': 0.0,
                }))
                move_vals['line_ids'].append((0, 0, {
                    'account_id': self.env['account.account'].search([
                        ('company_id', '=', self.env.company.id),
                        ('code', 'ilike', 'Intercompany Payable')
                    ], limit=1).id,
                    'debit': 0.0,
                    'credit': line.salary_portion,
                }))
            self.env['account.move'].create(move_vals)
