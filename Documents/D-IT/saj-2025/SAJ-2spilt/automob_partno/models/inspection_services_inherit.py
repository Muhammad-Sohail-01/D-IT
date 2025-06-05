import secrets
from odoo import api, fields, models, _
from markupsafe import Markup
from odoo.exceptions import ValidationError




class VehicleRequiredServices(models.Model):
    _inherit = 'vehicle.required.services'


    part_number_id = fields.Many2one('auto.mobile.product.product.partno.line', string="Part No")

    @api.onchange('part_number_id')
    def _onchange_part_nubmer_id(self):
        if not self.part_number_id:
            return

        # Check if the selected part number has a sale price
        if self.part_number_id.sale_price:
            self.price = self.part_number_id.sale_price
        else:
        # Fallback to the list price if there's no sale price
            self.price = self.product_id.lst_price 

    