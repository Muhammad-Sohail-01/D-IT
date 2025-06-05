# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrderLine(models.Model):
    """Inheriting sale order line for adding some fields"""
    _inherit = 'sale.order.line'

    order_line_image = fields.Binary(string="Image",
                                     related="product_id.image_1920",
                                     help='Corresponding image of product')
    contact_email = fields.Char(related="order_partner_id.email",
                                string='Email',
                                help='Email of the customer')
    contact_phone = fields.Char(related="order_partner_id.phone",
                                string='Phone',
                                help='Phone number of the customer')
