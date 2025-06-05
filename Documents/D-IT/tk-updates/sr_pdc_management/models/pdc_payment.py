# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_pdc_payment_account = fields.Many2one('account.account', 'PDC Payment Account for Customer')
    vendor_pdc_payment_account = fields.Many2one('account.account', 'PDC Payment Account for Vendors/Suppliers')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        #     res['customer_pdc_payment_account'] = int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account', default=0))
        #     res['vendor_pdc_payment_account'] = int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account', default=0))

      
        res['customer_pdc_payment_account'] = {
            'id': int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account', default=0))
        }
        res['vendor_pdc_payment_account'] = {
            'id': int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account', default=0))
        }

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('customer_pdc_payment_account', self.customer_pdc_payment_account.id)
        self.env['ir.config_parameter'].sudo().set_param('vendor_pdc_payment_account', self.vendor_pdc_payment_account.id)

        super(ResConfigSettings, self).set_values()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pdc_id = fields.Many2one('sr.pdc.payment', 'Post Dated Cheques')

class AccountMove(models.Model):
    _inherit = "account.move"

    pdc_id = fields.Many2one('sr.pdc.payment', 'Post Dated Cheques')

    # @api.depends(
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state')
    # def _compute_amount(self):
    #     invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
    #     self.env['account.payment'].flush(['state'])
    #     if invoice_ids:
    #         self._cr.execute(
    #             '''
    #                 SELECT move.id
    #                 FROM account_move move
    #                 JOIN account_move_line line ON line.move_id = move.id
    #                 JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
    #                 JOIN account_move_line rec_line ON
    #                     (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
    #                     OR
    #                     (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
    #                 JOIN account_payment payment ON payment.id = rec_line.payment_id
    #                 JOIN account_journal journal ON journal.id = rec_line.journal_id
    #                 WHERE payment.state IN ('posted', 'sent')
    #                 AND journal.post_at = 'bank_rec'
    #                 AND move.id IN %s
    #             ''', [tuple(invoice_ids)]
    #         )
    #         in_payment_set = set(res[0] for res in self._cr.fetchall())
    #     else:
    #         in_payment_set = {}
    #
    #     for move in self:
    #         total_untaxed = 0.0
    #         total_untaxed_currency = 0.0
    #         total_tax = 0.0
    #         total_tax_currency = 0.0
    #         total_residual = 0.0
    #         total_residual_currency = 0.0
    #         total = 0.0
    #         total_currency = 0.0
    #         currencies = set()
    #
    #         for line in move.line_ids:
    #             if line.currency_id:
    #                 currencies.add(line.currency_id)
    #
    #             if move.is_invoice(include_receipts=True):
    #                 # === Invoices ===
    #
    #                 if not line.exclude_from_invoice_tab:
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance
    #                     total_untaxed_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.tax_line_id:
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.account_id.user_type_id.type in ('receivable', 'payable'):
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #
    #         if move.type == 'entry' or move.is_outbound():
    #             sign = 1
    #         else:
    #             sign = -1
    #         if self._context.get('pdc'):
    #             total_residual = 0
    #         move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
    #         move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
    #         move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
    #         move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = -total
    #         move.amount_residual_signed = total_residual
    #
    #         currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
    #         is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual
    #
    #         # Compute 'invoice_payment_state'.
    #         if move.state == 'posted' and is_paid:
    #             if move.id in in_payment_set:
    #                 move.invoice_payment_state = 'in_payment'
    #             else:
    #                 move.invoice_payment_state = 'paid'
    #         else:
    #             move.invoice_payment_state = 'not_paid'


# # When you click on add in invoice then this method called
#     @api.multi
#     def assign_outstanding_credit(self, credit_aml_id):
#         self.ensure_one()
#         credit_aml = self.env['account.move.line'].browse(credit_aml_id)
#         if not credit_aml.currency_id and self.currency_id != self.company_id.currency_id:
#             amount_currency = self.company_id.currency_id._convert(credit_aml.balance, self.currency_id, self.company_id, credit_aml.date or fields.Date.today())
#             credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
#                 'amount_currency': amount_currency,
#                 'currency_id': self.currency_id.id})
#         if credit_aml.payment_id:
#             credit_aml.payment_id.write({'invoice_ids': [(4, self.id, None)]})
#         if credit_aml.pdc_id:
#             credit_aml.pdc_id.write({'invoice_ids': [(4, self.id, None)]})
#         return self.register_payment(credit_aml)



class PdcAccountPayment(models.Model):
    _name = "pdc.account.payment"
    _description = "PDC Account Payment"


    payment_id = fields.Many2one('account.payment',string="Payments")
    ref = fields.Char(string="Cheque Ref",related="payment_id.ref",store=True,readonly="1")
    amount = fields.Monetary(string="Amount",related="payment_id.amount",store=True,readonly="1")
    journal_id = fields.Many2one('account.journal',string="Journal",related="payment_id.journal_id",store=True,readonly="1")
    pdc_payment_id = fields.Many2one('sr.pdc.payment',string="PDC Payment")
    select_payment = fields.Boolean(string="Selct Payment")
    currency_id = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_id, store=True)
    payment_type = fields.Selection([('outbound','Outbound'),('inbound','Inbound'),('none','None')],store=True,compute="_compute_pdc_payment")

    @api.depends('pdc_payment_id','pdc_payment_id.payment_type','payment_id')
    def _compute_pdc_payment(self):
        for line in self:
            payment_type = 'none'
            if line.pdc_payment_id and line.pdc_payment_id.payment_type:
                payment_type = line.pdc_payment_id.payment_type
            line.payment_type = payment_type

    @api.model
    def create(self,vals):
        res = super(PdcAccountPayment,self).create(vals)
        if res.pdc_payment_id:
            get_payment_amount = res.pdc_payment_id.get_payment_amount()
            res.pdc_payment_id.update(get_payment_amount)
        return res

    def write(self,vals):
        res = super(PdcAccountPayment,self).write(vals)
        for payment in self:
            if payment.pdc_payment_id:
                get_payment_amount = payment.pdc_payment_id.get_payment_amount()
                payment.pdc_payment_id.update(get_payment_amount)
        return res

class PdcPayment(models.Model):
    _name = "sr.pdc.payment"
    
    def get_payment_amount(self):
        total_amount = 0
        cheque_ref = ''
        for line in self.pdc_account_payment_ids.filtered(lambda x:x.select_payment == True):
            total_amount += line.payment_id.amount
        cheque_ref = ', '.join(pdc_account.ref for pdc_account in self.pdc_account_payment_ids.filtered(lambda x:x.select_payment == True and x.ref))
        return {'amount':total_amount,'cheque_ref':cheque_ref}

    invoice_ids = fields.Many2many('account.move', 'account_invoice_pdc_rel', 'pdc_id', 'invoice_id', string="Invoices", copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('register', 'Registered'),('return', 'Returned'),('deposit', 'Deposited'),('bounce', 'Bounced'), ('done', 'Done'), ('cancel', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ['bank'])])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    cheque_ref = fields.Char('Cheque Reference')
    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    name = fields.Char('Name')
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True)
    unedit_payment_type = fields.Boolean(string="Payment")
    pdc_account_payment_ids = fields.One2many('pdc.account.payment','pdc_payment_id')

    @api.onchange('journal_id')
    def _default_currency(self):
        if self.journal_id:
            journal = self.journal_id
            currency_id = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
            self.currency_id= currency_id.id
        else:
            self.currency_id= False

    @api.model
    def default_get(self, default_fields):
        rec = super(PdcPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if 'default_payment_type' in self._context and self._context['default_payment_type'] in ('inbound','outbound'):
            rec['unedit_payment_type'] = True

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].move_type
        for inv in invoices[1:]:
            if inv.move_type != dtype:
                if ((dtype == 'in_refund' and inv.move_type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.move_type == 'in_refund')):
                    raise UserError(_("You cannot register Post dated cheques for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.move_type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.move_type == 'out_refund')):
                    raise UserError(_("You cannot register Post dated cheques for customer invoices and credit notes at the same time."))

        amount = abs(sum(invoices.mapped('amount_residual')))
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': amount,
            'payment_type': 'inbound' if amount > 0 else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'communication': invoices[0].payment_reference or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return rec

    def cancel(self):
        self.state = 'cancel'

    def register(self):
        inv = self.env['account.move'].browse(self._context.get('active_ids'))
        if inv:
            inv.amount_residual = 0
        self.state='register'
        if self.payment_type == 'inbound':
            self.name = self.env['ir.sequence'].next_by_code('pdc.payment')
        else:
            self.name = self.env['ir.sequence'].next_by_code('pdc.payment.vendor')
        return

    def return_cheque(self):
        self.state='return'
        return

    def deposit(self):
        if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
            inv = self.env['account.move'].browse(self._context.get('active_ids'))
            AccountMove = self.env['account.move'].with_context(default_move_type='entry')
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            if inv:
                inv.state = 'paid'
                custom_currency_id = inv.currency_id
                company_currency_id = inv.company_id.currency_id
                account_id = inv.account_id.id
            else:
                custom_currency_id = self.currency_id
                company_currency_id = self.env.user.company_id.currency_id
                if self.payment_type == 'inbound':
                    account_id = self.partner_id.property_account_receivable_id.id
                else:
                    account_id = self.partner_id.property_account_payable_id.id
            if self.currency_id != self.env.user.company_id.currency_id:
                balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id, self.due_date)
            else:
                balance = self.amount
            name = ''
            if self.invoice_ids:
                name += 'PDC Payment: '
                for record in self.invoice_ids:
                    if record.line_ids:
                        name += record.name + ', '
                name = name[:len(name) - 2]
            pdc_credit_account_id = False
            pdc_debit_account_id  = False
            if self.payment_type == 'inbound':
                pdc_credit_account_id = account_id
                pdc_debit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
            else:
                pdc_credit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
                pdc_debit_account_id = account_id
            if self.env.user.company_id.currency_id != self.currency_id:
                amount_currency = self.amount
            else:
                amount_currency = 0.0
            move_vals = {
                'date': self.due_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'partner_id': self.partner_id.id,
                'pdc_id' : self.id,
                'line_ids': [
                    (0, 0, {
                        'name': name,
                        'amount_currency': amount_currency,
                        'currency_id': self.currency_id.id,
                        'debit': 0.0,
                        'credit': balance ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_credit_account_id,
                        'pdc_id' : self.id,
                    }),
                    (0, 0, {
                        'name': name,
                        'amount_currency': -amount_currency,
                        'currency_id': self.currency_id.id,
                        'debit': balance,
                        'credit': 0.0 ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_debit_account_id,
                        'pdc_id' : self.id,
                    }),
                ],
            }
            move = AccountMove.create(move_vals)
            move.action_post()
        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        self.state = 'deposit'
        return True

    def done(self):
        if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            AccountMove = self.env['account.move'].with_context(default_move_type='entry')
            if self.currency_id != self.env.user.company_id.currency_id:
                balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id, self.due_date)
            else:
                balance = self.amount
            if self.payment_type == 'inbound':
                account_id = self.journal_id.company_id.account_journal_payment_debit_account_id.id
            else:
                account_id = self.journal_id.company_id.account_journal_payment_credit_account_id.id
            name = ''
            if self.invoice_ids:
                name += 'PDC Payment: '
                for record in self.invoice_ids:
                    if record.line_ids:
                        name += record.name + ', '
                name = name[:len(name) - 2]
            if self.payment_type == 'inbound':
                pdc_debit_account_id = account_id
                pdc_credit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
            else:
                pdc_credit_account_id = account_id
                pdc_debit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
            if self.env.user.company_id.currency_id != self.currency_id:
                amount_currency = self.amount
            else:
                amount_currency = 0.0
            move_vals = {
                'date': self.due_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'partner_id': self.partner_id.id,
                'line_ids': [
                    (0, 0, {
                        'name': name,
                        'amount_currency': amount_currency,
                        'currency_id': self.currency_id.id,
                        'debit': 0.0,
                        'credit': balance ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_credit_account_id,
                    }),
                    (0, 0, {
                        'name': name,
                        'amount_currency': -amount_currency,
                        'currency_id': self.currency_id.id,
                        'debit': balance,
                        'credit': 0.0 ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_debit_account_id,
                    }),
                ],
            }
            move = AccountMove.create(move_vals)
            move.action_post()
            pdc_move = self.env['account.move'].search([('pdc_id','=',self.id)])
            self.state = 'done'
            if self.invoice_ids:
                line_ids = (pdc_move + self.invoice_ids).line_ids \
                    .filtered(lambda line: not line.reconciled and line.account_id.id == self.partner_id.property_account_receivable_id.id)
                account_ids = line_ids.mapped('account_id.name')
                (pdc_move + self.invoice_ids).line_ids \
                    .filtered(lambda line: not line.reconciled and line.account_id.id == self.partner_id.property_account_receivable_id.id)\
                    .reconcile()
                line_ids = (pdc_move + move).line_ids \
                    .filtered(lambda line: not line.reconciled and (line.account_id.id == int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))) )
                (pdc_move + move).line_ids \
                    .filtered(lambda line: not line.reconciled and (line.account_id.id == int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))) )\
                    .reconcile()
        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        return True

    def bounce(self):
        if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
            if self.payment_type == 'inbound':
                account_id = self.partner_id.property_account_receivable_id.id
            else:
                account_id = self.partner_id.property_account_payable_id.id
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            AccountMove = self.env['account.move'].with_context(default_move_type='entry')
            if self.currency_id != self.env.user.company_id.currency_id:
                balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id, self.due_date)
            else:
                balance = self.amount
            name = ''
            if self.invoice_ids:
                name += 'PDC Payment: '
                for record in self.invoice_ids:
                    if record.line_ids:
                        name += record.name + ', '
                name = name[:len(name) - 2]
            if self.payment_type == 'inbound':
                pdc_debit_account_id = account_id
                pdc_credit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
            else:
                pdc_credit_account_id = account_id
                pdc_debit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
            if self.env.user.company_id.currency_id != self.currency_id:
                amount_currency = self.amount
            else:
                amount_currency = 0.0
            move_vals = {
                'date': self.due_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'partner_id': self.partner_id.id,
                'line_ids': [
                    (0, 0, {
                        'name': name,
                        'amount_currency': amount_currency,
                        'currency_id': self.currency_id.id,
                        'debit': 0.0,
                        'credit': balance ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_credit_account_id,
                    }),
                    (0, 0, {
                        'name': name,
                        'amount_currency': -amount_currency,
                        'currency_id': self.currency_id.id ,
                        'debit': balance,
                        'credit': 0.0 ,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_debit_account_id,
                    }),
                ],
            }
            move = AccountMove.create(move_vals)
            move.action_post()
            pdc_move = self.env['account.move'].search([('pdc_id','=',self.id)])
            if pdc_move:
                (pdc_move + move).line_ids \
                    .filtered(lambda line: not line.reconciled and line.account_id.id == self.partner_id.property_account_receivable_id.id)\
                    .reconcile()

                (pdc_move + move).line_ids \
                    .filtered(lambda line: not line.reconciled and (line.account_id.id == int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))) )\
                    .reconcile()

            self.state = 'bounce'
            for record in self.invoice_ids:
                record.amount_residual = record.amount_total

        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        return True        
