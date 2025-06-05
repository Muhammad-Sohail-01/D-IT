# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentPDC(models.Model):
    _inherit = "account.payment"

    is_pdc_payment = fields.Boolean (
        string='PDC Payment',

    )
    cheque_date = fields.Date(string="Cheque Date")
    cheque_number = fields.Char(string="Cheque Number")
    pdc_state = fields.Selection(
        [
            ("registered", "Registered"),
            ("deposited", "Deposited"),
            ("returned", "Returned"),
            # ("cancelled", "Cancelled"),
        ],
        string="PDC Status",
        default="registered",
        tracking=True,
    )
    deposit_date = fields.Date(string="Deposit Date")

    deposit_journal_id = fields.Many2one (
        'account.journal',
        string='Deposit Journal',
        domain="[('type', '=', 'bank'), ('allow_pdc', '=', False)]"
    )

    # journal_id = fields.Many2one (
    #     'account.journal',
    #     string='Journal',
    # )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=False):
        res = super ()._prepare_move_line_default_vals (write_off_line_vals=write_off_line_vals,
                                                        force_balance=force_balance)
        if self.is_pdc_payment and self.journal_id.allow_pdc:
            for line in res:
                # For customer payments (inbound)
                if self.partner_type == 'customer':
                    if line.get ('account_id') == self.partner_id.property_account_receivable_id.id:
                        line['credit'] = self.amount
                        line['account_id'] = self.partner_id.property_account_receivable_id.id
                    else:
                        line['debit'] = self.amount
                        line['account_id'] = self.journal_id.pdc_receivable_account_id.id

                # For vendor payments (outbound)
                elif self.partner_type == 'supplier':
                    if line.get ('account_id') == self.partner_id.property_account_payable_id.id:
                        line['debit'] = self.amount
                        line['account_id'] = self.partner_id.property_account_payable_id.id
                    else:
                        line['credit'] = self.amount
                        line['account_id'] = self.journal_id.pdc_payable_account_id.id
        return res

    def action_deposit_pdc(self):
        for payment in self:
            if not payment.deposit_journal_id or not payment.deposit_date:
                raise ValidationError (_ ('Please set deposit journal and date'))

            move_vals = {
                'date'      : payment.deposit_date,
                'journal_id': payment.deposit_journal_id.id,
                'ref'       : f'PDC Deposit - {payment.cheque_number}',
                'line_ids'  : []
            }

            if payment.partner_type == 'customer':
                move_vals['line_ids'].extend ([
                    (0, 0, {
                        'account_id': payment.journal_id.pdc_receivable_account_id.id,
                        'credit'    : payment.amount,
                        'partner_id': payment.partner_id.id,
                    }),
                    (0, 0, {
                        'account_id': payment.deposit_journal_id.default_account_id.id,
                        'debit'     : payment.amount,
                        'partner_id': payment.partner_id.id,
                    })
                ])
            else:  # supplier
                move_vals['line_ids'].extend ([
                    (0, 0, {
                        'account_id': payment.deposit_journal_id.default_account_id.id,
                        'credit'    : payment.amount,
                        'partner_id': payment.partner_id.id,
                    }),
                    (0, 0, {
                        'account_id': payment.journal_id.pdc_payable_account_id.id,
                        'debit'     : payment.amount,
                        'partner_id': payment.partner_id.id,
                    })
                ])

            move = self.env['account.move'].create (move_vals)
            move.action_post ()
            payment.pdc_state = 'deposited'




    @api.onchange ('is_pdc_payment')
    def _onchange_is_pdc_payment(self):
        if self.is_pdc_payment and self.journal_id and not self.journal_id.allow_pdc:
            self.journal_id = False
            return {
                'warning': {
                    'title'  : 'Invalid Journal',
                    'message': 'Please select a journal that allows PDC payments.'
                }
            }

    @api.onchange ('deposit_date', 'cheque_date')
    def _onchange_deposit_date(self):
        if self.deposit_date and self.cheque_date and self.deposit_date < self.cheque_date:
            self.deposit_date = False
            return {
                'warning': {
                    'title'  : 'Invalid Date',
                    'message': 'Deposit date cannot be earlier than cheque date.'
                }
            }

    def action_return_pdc(self):
        for payment in self:
            # Reverse original PDC entry
            payment.move_id._reverse_moves([{"date": fields.Date.today()}])
            payment.pdc_state = "returned"

            @api.onchange ('cheque_number', 'partner_id')
            def _onchange_cheque_number(self):
                if self.cheque_number and self.partner_id:
                    existing_cheque = self.env['account.payment'].search ([
                        ('cheque_number', '=', self.cheque_number),
                        ('partner_id', '=', self.partner_id.id),
                        ('id', '!=', self.id),
                        ('is_pdc_payment', '=', True)
                    ], limit=1)

                    if existing_cheque:
                        return {
                            'warning': {
                                'title'  : 'Duplicate Cheque Number',
                                'message': f'This cheque number is already used for this customer in payment {existing_cheque.name}. You can continue but please verify.'
                            }
                        }

    # def action_cancel_pdc(self):
    #     for payment in self:
    #         payment.pdc_state = "cancelled"
