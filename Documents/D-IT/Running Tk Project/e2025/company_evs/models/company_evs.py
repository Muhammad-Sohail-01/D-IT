# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Company Custom ID (4 Character Fixed Length)
    company_custom_id = fields.Char(
        string='Company Custom ID',
        size=4,
        required=True,
        copy=False,
        help='Unique 4-character identifier for the company'
    )

    # Company Short Code (4 Character Fixed Length)
    company_short_code = fields.Char(
        string='Company Short Code',
        size=4,
        required=True,
        copy=False,
        help='Unique 4-character short code for the company'
    )

    @api.constrains('company_custom_id', 'company_short_code')
    def _check_company_identifiers(self):
        """Ensure Company Custom ID and Short Code are unique and valid"""
        for record in self:
            # Check Custom ID
            if not record.company_custom_id or len(record.company_custom_id) != 4:
                raise ValidationError(_("Company Custom ID must be exactly 4 characters"))

            # Check Short Code
            if not record.company_short_code or len(record.company_short_code) != 4:
                raise ValidationError(_("Company Short Code must be exactly 4 characters"))

            # Check uniqueness of Custom ID
            existing_custom_id = self.search([
                ('company_custom_id', '=', record.company_custom_id),
                ('id', '!=', record.id)
            ])
            if existing_custom_id:
                raise ValidationError(_("Company Custom ID must be unique"))

            # Check uniqueness of Short Code
            existing_short_code = self.search([
                ('company_short_code', '=', record.company_short_code),
                ('id', '!=', record.id)
            ])
            if existing_short_code:
                raise ValidationError(_("Company Short Code must be unique"))


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.depends('code', 'name', 'company_id.company_custom_id')
    def _compute_display_name(self):
        for record in self:
            company_id_char = record.company_id.company_custom_id or ''
            record.display_name = f"{record.code}-{record.name}-{company_id_char}"


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.depends('name', 'company_id.company_short_code')
    def _compute_display_name(self):
        for record in self:
            company_short_code = record.company_id.company_short_code or ''
            record.display_name = f"{record.name} [{company_short_code}]"


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_unique_code = fields.Char(
        string='Asset Unique Code',
        copy=False,
        readonly=True,
        help='Unique asset code generated per company'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique asset code during asset creation"""
        for vals in vals_list:
            company_id = vals.get('company_id', self.env.company.id)
            company = self.env['res.company'].browse(company_id)

            sequence = self.env['ir.sequence']
            asset_code = sequence.next_by_code('asset.unique.code') or ''

            vals['asset_unique_code'] = f"{company.company_custom_id}-{asset_code}"

        return super().create(vals_list)

    @api.constrains('asset_unique_code')
    def _check_asset_unique_code(self):
        """Ensure asset unique code follows company-specific rules"""
        for record in self:
            if not record.asset_unique_code:
                raise ValidationError(_("Asset Unique Code generation failed"))

            parts = record.asset_unique_code.split('-')
            if len(parts) != 2 or len(parts[0]) != 4:
                raise ValidationError(_("Invalid Asset Unique Code format"))


    
            