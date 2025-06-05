# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    partno_line_id = fields.One2many('auto.mobile.partno.line','partno_product_id')
