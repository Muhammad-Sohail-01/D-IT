# -*- coding: utf-8 -*-
# Copyright (C) 2024-TODAY TechKhedut (<https://www.techkhedut.com>)
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class AdvancePaymentWizard(models.TransientModel):
    """Advance Payment Wizard"""
    _name = 'advance.payment.wizard'
    _description = __doc__

    @api.model
    def default_get(self, fields):
        res = super(AdvancePaymentWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['job_card_id'] = active_id
        advance_payment_journal_id = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.advance_payment_journal_id')
        if advance_payment_journal_id and isinstance(advance_payment_journal_id,
                                                     str) and advance_payment_journal_id.isdigit():
            advance_payment_journal_id = int(advance_payment_journal_id)

        res['journal_id'] = advance_payment_journal_id

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
        }
        payment_id = self.env['account.payment'].create(payment_data)

        advance_payment_status = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.advance_payment_status')
        if advance_payment_status == 'posted':
            payment_id.action_post()

        self.job_card_id.advance_payment_id = payment_id.id
