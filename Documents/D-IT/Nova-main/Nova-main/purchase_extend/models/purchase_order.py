
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    ref_number = fields.Char(string="Reference Number")
    car_service_id = fields.Many2one('car.history', string="Car Plate No.")
    
    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res.update({
            'ref_number': self.ref_number,
            'car_service_id': self.car_service_id.id,
            })
        return res