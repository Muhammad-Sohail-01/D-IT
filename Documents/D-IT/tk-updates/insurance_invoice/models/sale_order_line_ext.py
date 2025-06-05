from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_insurance = fields.Boolean(
        string="Is Insurance")

