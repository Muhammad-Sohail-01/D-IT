# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

from odoo.tools.populate import compute


class CompanyUniqueCode(models.Model):
    _inherit = 'account.asset'

    asset_code = fields.Char(string="Asset Code",)
    asset_number = fields.Char(string="Asset Number", readonly=True,)

    # @api.onchange('model_id')
    # def _onchange_model_id(self):
    #     if self.model_id:
    #         self.asset_code = self.model_id.asset_code
    #     else:
    #         self.asset_code = ' '
    # _sql_constraints = [
    #     ('asset_code', 'unique(asset_code)', 'Code must be unique per Asset!'),
    # ]

    # @api.depends('company_id', 'asset_code')
    # def _compute_asset_number(self):
    #     for record in self:
    #         if record.company_id and record.asset_code:
    #             company_code = record.company_id.unique_code
    #             print(company_code)
    #             record.asset_number = f"{company_code}/{record.asset_code}"

    # @api.model
    # def create(self, vals):
    #     # Ensure company_id and asset_code are provided
    #     company_id = vals.get('company_id')
    #     asset_code = vals.get('asset_code')
    #
    #     # Fetch company code if company_id is present
    #     if company_id:
    #         company = self.env['res.company'].browse(company_id)
    #         company_code = company.unique_code if company else ''
    #     else:
    #         company_code = ''
    #
    #     # Generate the sequence
    #     seq = self.env['ir.sequence'].next_by_code('account.asset')
    #
    #     # Build the asset_number
    #     asset_number = (company_code + '-') + (asset_code+'-') + str(seq)
    #
    #     # Add asset_number to vals
    #     vals['asset_number'] = asset_number
    #
    #     # Create the record
    #     return super(CompanyUniqueCode, self).create(vals)




