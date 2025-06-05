# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CompanyGroup(models.Model):
    _name = 'company.group'
    _description = 'Company Group'

    name = fields.Char(string='Group Name', required=True)
    company_ids = fields.Many2many('res.company', string='Companies in Group')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_group_ids = fields.Many2many(
        'company.group',
        string="Company Groups",
        help="Select company groups to automatically fill allowed companies"
    )
    allowed_company_ids = fields.Many2many(
        'res.company',
        string="Allowed Companies",
        help="Companies that can see this product"
    )

    @api.onchange('company_group_ids')
    def _onchange_company_group_ids(self):
        if self.company_group_ids:
            companies = self.env['res.company']
            for group in self.company_group_ids:
                companies |= group.company_ids
            self.allowed_company_ids = companies

# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#     company_group_ids = fields.Many2many(
#         'company.group',
#         string="Company Groups",
#         help="Select company groups to automatically fill allowed companies"
#     )
#     allowed_company_ids = fields.Many2many(
#         'res.company',
#         string="Allowed Companies",
#         help="Companies that can see this product"
#     )
#
#     @api.onchange('company_group_ids')
#     def _onchange_company_group_ids(self):
#         if self.company_group_ids:
#             companies = self.env['res.company']
#             for group in self.company_group_ids:
#                 companies |= group.company_ids
#             self.allowed_company_ids = companies
