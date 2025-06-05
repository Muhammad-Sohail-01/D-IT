# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CompanyUniqueCode(models.Model):
    _inherit = 'account.asset'

    asset_code = fields.Char(string="Asset Code", required=True)
    asset_number = fields.Char(string="Asset Number", store=True, compute='_compute_asset_number')
    sequence_number = fields.Char('Sequence Number', required=True, index='trigram', copy=False, default='New')

    _sql_constraints = [
        ('asset_code', 'unique(asset_code)', 'Code must be unique per Asset!'),
    ]

    @api.depends('company_id', 'asset_code')
    def _compute_asset_number(self):
        for record in self:
            if record.company_id and record.asset_code:
                company_code = record.company_id.unique_code
                record.asset_number = f"{company_code}/{record.asset_code}/{record.sequence_number}"

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_number'] = self.env['ir.sequence'].next_by_code('account.asset')
        return super(CompanyUniqueCode, self).create(vals)

         

    
            