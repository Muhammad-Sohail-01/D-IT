from odoo import api, fields, models


class VehicleResCompnay(models.Model):
    _inherit = 'res.company'

    part_warehouse_id = fields.Many2one('stock.warehouse', string="Part Warehouse")
