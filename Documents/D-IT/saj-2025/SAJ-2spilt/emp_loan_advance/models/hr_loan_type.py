from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime



class HrLoanType (models.Model):
    _name = 'hr.loan.type'
    _description = 'Loan Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char (
        required=True,
        tracking=True)

    sequence = fields.Integer (
        default=10,
        help="Determine the display order")

    active = fields.Boolean (
        default=True,
        tracking=True)

    description = fields.Html (
        string='Description',
        help="Detailed description of the loan type and its terms")

    max_amount = fields.Monetary (
        string='Maximum Amount',
        currency_field='currency_id',
        required=True,
        tracking=True)

    currency_id = fields.Many2one (
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True)

    max_installments = fields.Integer (
        string='Maximum Installments',
        required=True,
        tracking=True)


    min_employment_months = fields.Integer (
        string='Minimum Employment (Months)',
        default=0,
        help="Minimum months of employment required to be eligible")

    max_active_loans = fields.Integer (
        string='Maximum Active Loans',
        default=1,
        help="Maximum number of active loans of this type allowed per employee")

    minimum_salary = fields.Monetary (
        string='Minimum Salary Required',
        currency_field='currency_id',
        help="Minimum salary required to be eligible for this loan type")

    salary_deduction_limit = fields.Float (
        string='Salary Deduction Limit (%)',
        default=00.00,
        help="Maximum percentage of salary that can be deducted for loan installments")

    hr_approvers_ids = fields.Many2many (
        'hr.employee',
        'loan_type_hr_rel',
        string='HR Approvers')

    finance_approvers_ids = fields.Many2many (
        'hr.employee',
        'loan_type_finance_rel',
        string='Finance Approvers')

    management_approvers_ids = fields.Many2many (
        'hr.employee',
        'loan_type_management_rel',
        string='Management Approvers')
    min_accountant_approval = fields.Integer (
        string='Minimum Accountant Approvals',
        default=1)
    min_finance_approval = fields.Integer (
        string='Minimum Finance Approvals',
        default=1)
    min_management_approval = fields.Integer (
        string='Minimum Management Approvals',
        default=1)
    requires_accountant = fields.Boolean (
        string='Requires Accountant Approval',
        default=False)
    requires_finance = fields.Boolean(
        string='Requires Finance Approval',
        default=False)
    requires_management = fields.Boolean(
        string='Requires Management Approval',
        default=False)

    max_installment_count = fields.Integer(
        string='Maximum Installment Count',
        default=1)


    _sql_constraints = [
        ('positive_max_amount',
         'CHECK(max_amount > 0)',
         'Maximum amount must be greater than zero'),
        ('positive_max_installments',
         'CHECK(max_installments > 0)',
         'Maximum installments must be greater than zero'),

    ]

    @api.constrains ('salary_deduction_limit')
    def _check_salary_deduction_limit(self):
        for record in self:
            if record.salary_deduction_limit <= 0 or record.salary_deduction_limit > 100:
                raise ValidationError (_ ('Salary deduction limit must be between 0 and 100 percent'))
