# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    partno_line_id = fields.One2many(
    'auto.mobile.product.product.partno.line', 
    'partno_product_id', 
    readonly=False  # Make it writable
)

