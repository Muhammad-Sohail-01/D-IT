# -*- coding: utf-8 -*-

from odoo import models


class HrPayslip(models.Model):
    """ Model for adding advance salary computations in hr_payslip. """
    _inherit = 'hr.payslip'

    def input_data_salary_line(self, name, amount):
        """ Set updated values to other input lines. """
        check_lines = []
        input_type = self.env['hr.payslip.input.type'].search([
            ('input_id', '=', name)])
        line = (0, 0, {
            'input_type_id': input_type.id,
            'amount': amount,
        })
        check_lines.append(line)
        self.input_line_ids = check_lines

    def compute_sheet(self):
        """ Method for inherit and adding advance salary input line in
        payslip lines"""
        salary_line = self.struct_id.rule_ids.filtered(
                        lambda x: x.code == 'SAR')
        if salary_line:
            get_amount = self.env['salary.advance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approve')
            ])
            if get_amount:
                if self.date_from <= get_amount.date <= self.date_to:
                    amount = get_amount.advance
                    name = salary_line.id
                    code = salary_line.code
                    if (code not in self.input_line_ids.mapped('input_type_id').
                            mapped('code')):
                        self.input_data_salary_line(name, amount)
        return super(HrPayslip, self).compute_sheet()
