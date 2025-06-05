# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CompanyUniqueCode(models.Model):
    _inherit = 'res.company'

    unique_code = fields.Char(string="Company Code", default=3, required=True)
    unique_code_no = fields.Char(string="Company Code No", default=3)
    # @api.model
    # def create(self, vals):
    #     if not vals.get('unique_code'):
    #         raise ValidationError(_('Company Code is required and must be unique %s character'))
    #     # if len(vals.get('unique_id')) != self.env.user.company_id.asset_id_length:
    #     #     raise ValidationError(_('Company ID must be unique %s character') % self.env.user.company_id.asset_id_length)
    #     if self.search([('unique_code','=',vals.get('unique_code'))]):
    #         raise ValidationError(_('Company Code already exists'))
    #     return super(CompanyUniqueCode, self).create(vals)

#   sql constraint will handle unique code function
#     _sql_constraints = [
#         ('code_uniq', 'unique(unique_code)', 'Code must be unique per Company!'),
#         ]
