from odoo import models, fields, api, _


class FixedAssetModelName(models.Model):
    _inherit = 'account.asset'

    # comp_account_code = fields.Char(related='company_id.unique_code', store=True)
    comp_alpha = fields.Char(related='company_id.unique_alpha', store=True)
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name}[{rec.comp_account_code} ]"
