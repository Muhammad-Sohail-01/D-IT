# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allowed_company_ids = fields.Many2many(
        'res.company',
        string="Allowed Companies",
        help="Companies that can see this product"
    )

class ResPartner(models.Model):
    _inherit = 'res.partner'

    allowed_company_ids = fields.Many2many(
        'res.company',
        string="Allowed Companies",
        help="Companies that can see this product"
    )


