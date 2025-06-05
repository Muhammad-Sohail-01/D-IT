from odoo import models, fields, api, _


class ChartOfAccountCode(models.Model):
    _inherit = 'account.account'

    comp_account_code = fields.Char(related='company_id.unique_code', store=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} {rec.name}[{rec.comp_account_code} ]"


# year = fields.Char(string="Year", size=4, check_year=True)
#
#     @api.constrains('year')
#     def _check_year(self):
#         for rec in self:
#             if rec.year and not 1900 <= int(rec.year) <= 2100:
#                 raise ValidationError(_("Year must be between 1900 and 2100"))

