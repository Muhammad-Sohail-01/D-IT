from odoo import api, fields, models


class VehicleResCompnay(models.Model):
    _inherit = 'res.company'

    part_warehouse_id = fields.Many2one('stock.warehouse', string="Part Warehouse",)
    
    is_direct_quote = fields.Boolean(
        string="Direct Quote Approval",
        default=True,
        help="If enabled, allows direct quote approval without additional checks"
    )
