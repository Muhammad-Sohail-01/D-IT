from odoo import models, fields, api, _


class ChartOfAccountCode(models.Model):
    _inherit = 'account.account'

    comp_account_code = fields.Char(related='company_id.unique_code', store=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} {rec.name} [{rec.comp_account_code}]"
