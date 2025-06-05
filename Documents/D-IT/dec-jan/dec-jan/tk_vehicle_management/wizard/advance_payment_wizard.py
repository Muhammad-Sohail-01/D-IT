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



    @api.depends('journal_id')
    def _compute_available_payment_method_line_ids(self):
        for record in self:
            if record.journal_id:
                # Fetch available payment methods for the selected journal
                payment_method_lines = record.journal_id._get_available_payment_method_lines('inbound')  # 'outbound' or 'inbound'
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
        payment_data = {
            'payment_type': 'inbound',
            'partner_id': self.job_card_id.customer_id.id,
            'amount': self.amount,
            'date': fields.Date.today(),
            'ref': self.job_card_id.name,
            'journal_id': self.journal_id.id,
            'company_id': self.job_card_id.company_id.id,
        }
        payment_id = self.env['account.payment'].create(payment_data)

        advance_payment_status = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.advance_payment_status')
        if advance_payment_status == 'posted':
            payment_id.action_post()

        self.job_card_id.advance_payment_id = payment_id.id
