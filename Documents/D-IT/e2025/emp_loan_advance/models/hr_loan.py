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

    name = fields.Char (
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _ ('New'))

    employee_id = fields.Many2one (
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True)

    department_id = fields.Many2one (
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True)

    loan_amount = fields.Monetary (
        string='Loan Amount',
        required=True,
        tracking=True)

    currency_id = fields.Many2one (
        'res.currency',
        string='Currency',
        required=True,
        default=_get_default_currency)

    date_request = fields.Date (
        string='Request Date',
        default=fields.Date.context_today,
        required=True)

    loan_type_id = fields.Many2one (
        'hr.loan.type',
        string='Loan Type',
        required=True)

    installment_count = fields.Integer (
        string='Number of Installments',
        required=True,
        tracking=True)

    state = fields.Selection ([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get ('name', _ ('New')) == _ ('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code ('hr.loan') or _ ('New')
        return super ().create (vals_list)

    def action_submit(self):
        self.ensure_one ()
        self.write ({'state': 'submitted'})

    def action_approve(self):
        self.ensure_one ()
        if not self.env.user.has_group ('hr_loan.group_loan_manager'):
            raise ValidationError (_ ("You don't have the rights to approve loans."))
        self.write ({'state': 'approved'})

    def _compute_access_url(self):
        super ()._compute_access_url ()
        for loan in self:
            loan.access_url = f'/my/loans/{loan.id}'