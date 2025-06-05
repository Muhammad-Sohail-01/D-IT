from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
class HrLoanInstallment (models.Model):
    _name = 'hr.loan.installment'
    _description = 'Loan Installment'
    _order = 'sequence, id'

    loan_id = fields.Many2one(
        'hr.loan',
        string='Loan',
        required=True,
        ondelete='cascade')

    sequence = fields.Integer(
        string='Sequence',
        default=10)
    installment_date = fields.Date(
        string='Due Date',
        required=True)
    amount = fields.Float(
        string='Amount',
        required=True)
    paid_amount = fields.Float(
        string='Paid Amount',
        default=0.0)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')
    ], string='Status', default='draft', compute='_compute_state', store=True)

    @api.depends ('amount', 'paid_amount')
    def _compute_state(self):
        for record in self:
            if record.paid_amount == 0:
                record.state = 'draft'
            elif record.paid_amount >= record.amount:
                record.state = 'paid'
            else:
                record.state = 'partial'
