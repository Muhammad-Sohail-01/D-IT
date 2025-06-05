from odoo import api, fields, models, _
from odoo.exceptions import ValidationError




class VehicleRequiredParts(models.Model):
    _inherit = 'vehicle.required.parts'

    discount = fields.Float(digits=0, default=0.0)



    @api.depends('product_id', 'uom_id', 'qty')
    def _compute_discount(self):
        for line in self:
            if not line.product_id or line.display_type:
                line.discount = 0.0

            if not (
                line.order_id.pricelist_id
                and line.order_id.pricelist_id.discount_policy == 'without_discount'
            ):
                continue

            line.discount = 0.0

            if not line.pricelist_item_id:
                # No pricelist rule was found for the product
                # therefore, the pricelist didn't apply any discount/change
                # to the existing sales price.
                continue

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown to the customer
                    line.discount = discount



