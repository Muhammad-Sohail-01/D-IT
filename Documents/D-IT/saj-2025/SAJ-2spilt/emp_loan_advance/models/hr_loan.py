from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HrLoan (models.Model):
    _name = 'hr.loan'
    _description = 'Employee Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    def _get_default_currency(self):
        return self.env.company.currency_id

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _ ('New'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True)

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True)

    loan_amount = fields.Monetary(
        string='Loan Amount',
        required=True,
        tracking=True)

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=_get_default_currency)

    date_request = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
        required=True)

    loan_type_id = fields.Many2one(
        'hr.loan.type',
        string='Loan Type',
        required=True)

    installment_count = fields.Integer(
        string='Number of Installments',
        required=True,
        tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    installment_start_date = fields.Date(
        string='Installment Start Date',
        required=True,
        default=fields.Date.context_today)

    installment_line_ids = fields.One2many(
        'hr.loan.installment',
        'loan_id',
        string='Installments')

    hr_approval_ids = fields.Many2many(
        'hr.employee',
        'loan_hr_approval_rel',
        string='Hr Approvals')
    finance_approval_ids = fields.Many2many(
        'hr.employee',
        'loan_finance_approval_rel',
        string='Finance Approvals')
    management_approval_ids = fields.Many2many(
        'hr.employee',
        'loan_management_approval_rel',
        string='Management Approvals')

    accountant_approval_count = fields.Integer(
        compute='_compute_approval_counts')
    finance_approval_count = fields.Integer(
        compute='_compute_approval_counts')
    management_approval_count = fields.Integer(
        compute='_compute_approval_counts')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _ ('New')) == _ ('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan') or _ ('New')
        return super().create(vals_list)

    def action_submit(self):
        self.ensure_one()
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.ensure_one()
        if not self.env.user.has_group('hr_loan.group_loan_manager'):
            raise ValidationError(_ ("You don't have the rights to approve loans."))
        self.write({'state': 'approved'})

    @api.depends('accountant_approval_ids', 'finance_approval_ids', 'management_approval_ids')
    def _compute_approval_counts(self):
        for loan in self:
            loan.accountant_approval_count = len(loan.accountant_approval_ids)
            loan.finance_approval_count = len(loan.finance_approval_ids)
            loan.management_approval_count = len(loan.management_approval_ids)

    def action_submit(self):
        self.ensure_one()
        if not self.installment_line_ids:
            self._compute_installments()
        self.write({'state': 'submitted'})

    @api.onchange('loan_amount', 'installment_count', 'installment_start_date')
    def _onchange_loan_details(self):
        if self.loan_amount and self.installment_count and self.installment_start_date:
            self._compute_installments()

    def _compute_installments(self):
        self.ensure_one()
        installment_amount = self.loan_amount / self.installment_count
        installment_date = self.installment_start_date

        installment_vals = []
        for i in range(self.installment_count):
            installment_vals.append({
                'loan_id': self.id,
                'installment_date': installment_date,
                'amount': installment_amount,
                'sequence': i + 1,
            })
            installment_date = installment_date + relativedelta(months=1)

        self.installment_line_ids = [(5, 0, 0)]  # Clear existing lines
        self.installment_line_ids = [(0, 0, val) for val in installment_vals]

    # def _compute_access_url(self):
    #     super()._compute_access_url()
    #     for loan in self:
    #         loan.access_url = f'/my/loans/{loan.id}'
