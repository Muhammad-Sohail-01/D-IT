# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountPaymentRegisterPDC(models.TransientModel):
    _inherit = 'account.payment.register'

    is_pdc_payment = fields.Boolean(string='PDC Payment')
    cheque_date = fields.Date(string='Cheque Date')
    cheque_number = fields.Char(string='Cheque Number')
    pdc_state = fields.Selection([
        ('registered', 'Registered'),
        ('deposited', 'Deposited'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled')
    ], string='PDC Status', default='registered')

    @api.onchange('is_pdc_payment')
    def _onchange_is_pdc_payment(self):
        if self.is_pdc_payment:
            return {'domain': {'journal_id': [('allow_pdc', '=', True)]}}
        return {'domain': {'journal_id': []}}

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        if self.is_pdc_payment:
            payment_vals.update({
                'is_pdc_payment': True,
                'cheque_date': self.cheque_date,
                'cheque_number': self.cheque_number,
                'pdc_state': 'registered'
            })
        return payment_vals