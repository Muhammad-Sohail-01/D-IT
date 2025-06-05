# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
class AccountJournalPDC(models.Model):
    _inherit = 'account.journal'

    allow_pdc = fields.Boolean(string='Allow PDC')
    pdc_receivable_account_id = fields.Many2one(
        'account.account',
        string='PDC Receivable Account',
        domain=[('deprecated', '=', False)]
    )
    pdc_payable_account_id = fields.Many2one(
        'account.account',
        string='PDC Payable Account',
        domain=[('deprecated', '=', False)]
    )

    @api.onchange('allow_pdc')
    def _onchange_allow_pdc(self):
        if not self.allow_pdc:
            self.pdc_receivable_account_id = False
            self.pdc_payable_account_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('allow_pdc') and (not vals.get('pdc_receivable_account_id')
                                          or not vals.get('pdc_payable_account_id')):
                raise ValidationError(_('PDC accounts are required when PDC is allowed'))
        return super().create(vals_list)