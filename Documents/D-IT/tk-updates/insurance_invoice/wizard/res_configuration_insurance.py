# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    insurance_journal_id = fields.Many2one('account.journal')

    def set_values(self):
        super().set_values()
        re = self.env['ir.config_parameter'].sudo()
        # Store the insurance journal ID
        re.set_param('insurance_invoice.insurance_journal_id', self.insurance_journal_id.id)

    def get_values(self):
        res = super().get_values()
        re = self.env['ir.config_parameter'].sudo()
        # Retrieve the insurance journal ID
        journal_id = int(re.get_param('insurance_invoice.insurance_journal_id', default=0))
        # Use browse to get the record if it exists
        if journal_id:
            res['insurance_journal_id'] = journal_id
        else:
            res['insurance_journal_id'] = False
        return res
