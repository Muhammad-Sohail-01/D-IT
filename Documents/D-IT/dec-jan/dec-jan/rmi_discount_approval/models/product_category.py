# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    desc_limit = fields.Float(string="Discount Limit(%)",
                              help="If it is specified, the user can't give a discount greater than the specified amount")

