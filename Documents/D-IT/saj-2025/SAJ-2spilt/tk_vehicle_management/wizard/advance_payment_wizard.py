# -*- coding: utf-8 -*-
# Copyright (C) 2024-TODAY TechKhedut (<https://www.techkhedut.com>)
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class AdvancePaymentWizard(models.TransientModel):
    """Advance Payment Wizard"""
    _name = 'advance.payment.wizard'
    _description = __doc__

    line_ids = fields.Many2many('account.move.line', string="Journal Items")

    @api.model
    def default_get(self, fields_list):
        # Retrieve default values for the wizard
        res = super(AdvancePaymentWizard, self).default_get(fields_list)

        # Get the active_id from context, assuming it's for a job card
        active_id = self._context.get('active_id')
        res['job_card_id'] = active_id

        # Attempt to retrieve the journal for the active company
        advance_payment_journal_id = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.advance_payment_journal_id')
        
        # Ensure the journal ID is for the current company
        company_journals = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('type', 'in', ('bank', 'cash')),
        ])

        if advance_payment_journal_id and advance_payment_journal_id.isdigit():
            journal_id = int(advance_payment_journal_id)
            # Check if the journal exists and belongs to the active company
            journal = self.env['account.journal'].browse(journal_id)
            if journal.exists() and journal in company_journals:
                res['journal_id'] = journal_id
            else:
                # If journal is not found or does not match, pick the first available journal for the company
                res['journal_id'] = company_journals[:1].id
        else:
            
            res['journal_id'] = company_journals[:1].id if company_journals else False

        # Set user access rights for the accounting advance payment group
        res['is_accounting_advance_payment_user'] = self.env.user.has_group(
            'tk_vehicle_management.vehicle_accounting_advance_payment'
        )

        if self.env.user.has_group('tk_vehicle_management.vehicle_accounting_advance_payment'):
            res['is_accounting_advance_payment_user'] = True
        else:
            res['is_accounting_advance_payment_user'] = False
        return res

    journal_id = fields.Many2one('account.journal', domain="[('id', 'in', available_journal_ids)]")
    available_journal_ids = fields.Many2many('account.journal',
                                             compute="_compute_available_journal_ids")
    amount = fields.Monetary(currency_field="currency_id")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')
    job_card_id = fields.Many2one('vehicle.inspection')

    is_accounting_advance_payment_user = fields.Boolean()


    payment_method_line_id = fields.Many2one(
        'account.payment.method.line',
        string='Payment Method',
        domain="[('id', 'in', available_payment_method_line_ids)]",
        help="Select a payment method available for the selected journal."
    )
    available_payment_method_line_ids = fields.Many2many(
        'account.payment.method.line',
        compute='_compute_available_payment_method_line_ids',
        store=False  # Make it non-stored if you don’t need it in the database
    )

    selected_payment_type = fields.Selection ([
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('card', 'card'),
        ('tabby', 'TABBY'),
        ('payment_link', 'PAYMENT LINK'),
        ('cheque', 'PDC'),
    ], string='Selected Payment Type')

    @api.onchange ('selected_payment_type')
    def _onchange_selected_payment_type(self):
        if self.selected_payment_type:
            # Map payment types to journals and payment methods
            journal_mapping = {
                'cash': ('cash', 'cash'),
                'transfer': ('bank', 'bank transfer'),
                'card': ('bank', 'card'),
                'tabby': ('bank', 'tabby'),
                'payment_link': ('bank', 'payment link'),
                'cheque': ('bank', 'cheque'),
            }

            journal_type, payment_method = journal_mapping.get (self.selected_payment_type)

            # Find appropriate journal
            domain = [('type', '=', journal_type), ('company_id', '=', self.company_id.id)]
            journal = self.env['account.journal'].search (domain, limit=1)
            if journal:
                self.journal_id = journal.id

                # Find appropriate payment method line
                payment_method_line = journal.inbound_payment_method_line_ids.filtered (
                    lambda l: l.name.lower () == payment_method
                )
                if payment_method_line:
                    self.payment_method_line_id = payment_method_line.id

    def set_payment_method(self):
        """Set the selected payment method"""
        payment_type = self.env.context.get ('payment_type')
        self.selected_payment_type = payment_type
        self._onchange_selected_payment_type()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('journal_id')
    def _compute_available_payment_method_line_ids(self):
        for record in self:
            if record.journal_id:
                # Fetch available payment methods for the selected journal
                payment_method_lines = record.journal_id._get_available_payment_method_lines('inbound')
                # 'outbound' or 'inbound'
                record.available_payment_method_line_ids = payment_method_lines
            else:
                record.available_payment_method_line_ids = False

    @api.depends('journal_id')
    def _compute_available_journal_ids(self):
        """
        Get all journals having at least one payment method for inbound/outbound depending on the payment_type.
        """
        journals = self.env['account.journal'].search([
            '|',
            ('company_id', 'parent_of', self.env.company.id),
            ('company_id', 'child_of', self.env.company.id),
            ('type', 'in', ('bank', 'cash')),
        ])
        for pay in self:
            pay.available_journal_ids = journals.filtered('inbound_payment_method_line_ids')

    def action_create_advance_payment(self):
        """Take advance payment wizard"""
        if not self.env['ir.config_parameter'].sudo().get_param(
                'tk_vehicle_management.advance_payment_journal_id'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Missing Journal!'),
                    'message': _(
                        'Please first configure advance payment journal in Settings > Vehicle Repair'),
                    'sticky': False,
                }
            }
        if not self.payment_method_line_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _ ('Missing Payment Method!'),
                    'message': _ ('Please select a payment method.'),
                    'sticky': False,
                }
            }
        payment_data = {
            'payment_type': 'inbound',
            'partner_id': self.job_card_id.customer_id.id,
            'amount': self.amount,
            'date': fields.Date.today(),
            'ref': self.job_card_id.name,
            'journal_id': self.journal_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'company_id': self.job_card_id.company_id.id,
        }
        payment_id = self.env['account.payment'].create(payment_data)

        advance_payment_status = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.advance_payment_status')
        if advance_payment_status == 'posted':
            payment_id.action_post()

        self.job_card_id.advance_payment_id = payment_id.id
