# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class HrSalaryDistribution (models.Model):
    _name = 'hr.salary.distribution'
    _description = 'Salary Distribution'
    _inherit = ['mail.thread']

    payslip_id = fields.Many2one (
        'hr.payslip',
        string="Payslip",
        required=True,
        tracking=True
    )
    employee_id = fields.Many2one (
        'hr.employee',
        string="Employee",
        related='payslip_id.employee_id',
        readonly=True,
        store=True,
        tracking=True
    )

    payslip_company_id = fields.Many2one (
        'res.company',
        string="Payslip Company",
        related='payslip_id.company_id',
        store=True,
        readonly=True,
        tracking=True
    )

    company_id = fields.Many2one (
        'res.company',
        string="Distributed Company",
        required=True,
        tracking=True
    )
    salary_portion = fields.Float (
        string="Salary Portion",
        compute="_compute_salary_portion",
        store=True,
        tracking=True
    )
    percentage = fields.Float (
        string="Percentage",
        compute="_compute_percentage",
        inverse="_set_percentage",
        store=True,
        tracking=True
    )
    work_days = fields.Integer (
        string="Working Days",
        default=0,
        help="Manually input the working days. This will update the percentage.",
        tracking=True
    )
    total_period_days = fields.Float (
        string="Total Period Working Days",
        compute='_compute_total_period_days',
        store=True,
        help="Total working days in the period based on payslip worked days"
    )

    @api.depends ('payslip_id', 'payslip_id.worked_days_line_ids')
    def _compute_total_period_days(self):
        for record in self:
            total_days = 0.0
            if record.payslip_id:
                # Sum up all worked days from payslip worked days lines
                worked_days_lines = record.payslip_id.worked_days_line_ids
                total_days = sum (line.number_of_days for line in worked_days_lines)
            record.total_period_days = total_days

    @api.depends ('percentage', 'employee_id')
    def _compute_salary_portion(self):
        for record in self:
            cost_input = record.employee_id.cost_input if record.employee_id else 0.0
            record.salary_portion = (cost_input * record.percentage) / 100 if cost_input else 0.0

    @api.depends ('work_days', 'total_period_days')
    def _compute_percentage(self):
        for record in self:
            if record.total_period_days:
                record.percentage = (record.work_days / record.total_period_days) * 100 \
                if record.total_period_days else 0.0

    def _set_percentage(self):
        for record in self:
            if record.total_period_days:
                record.work_days = int ((record.percentage * record.total_period_days) / 100)

    @api.constrains ('percentage', 'work_days')
    def _check_distribution_constraints(self):
        for record in self:
            distributions = self.search ([('payslip_id', '=', record.payslip_id.id)])
            total_percentage = sum (d.percentage for d in distributions)
            total_work_days = sum (d.work_days for d in distributions)

            if round (total_percentage, 2) > 100.01:
                raise ValidationError (_ (
                    "Total percentage for all distributions (%.2f%%) cannot exceed 100%%.\n"
                    "Please adjust the percentages or working days." % total_percentage
                ))

            if total_work_days > record.total_period_days:
                raise ValidationError (_ (
                    "Total working days (%d) cannot exceed the available working days (%.1f) in the payslip period." %
                    (total_work_days, record.total_period_days)
                ))