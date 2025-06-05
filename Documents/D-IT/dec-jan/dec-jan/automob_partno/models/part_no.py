from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

from odoo.addons.base.models.ir_http import FasterRule

import logging
_logger = logging.getLogger(__name__)

# Model to manage part numbers
class PartNo(models.Model):
    _name = 'auto.mobile.partno.line'
    _description = 'Part No'
    _rec_name = 'partno'

    

    partno = fields.Char(string="Part No")
    partno_id = fields.Many2one('product.template', string="Product Template")
    partno_product_id = fields.Many2one('product.product', string="Product", store=True,)
    part_internal_no = fields.Char(string="Internal No", compute="_compute_formula_field", store=True)
    part_vendor_name = fields.Char(string="Vendor Name")
    part_type = fields.Selection(
        [('i', 'I'), ('o', 'O'), ('g', 'G'), ('h', 'H')],
        string='Type'
    )
    
    part_cat1 = fields.Many2many('item.catalog', 'item_catalog_rel', string="MAIN CATEGORY")
    part_cat2 = fields.Many2many('item.catalog', 'item_catalog2_rel', string="SUB CATEGORY")
    part_cat3 = fields.Many2many('item.catalog', 'item_catalog3_rel', string="PART ELEMENT")
    part_cat4 = fields.Many2many('item.catalog', 'item_catalog4_rel', string="CATALOG NAME")
    note = fields.Char(string="Note")
    # # Many2many relationship with car brands
    brand_ids = fields.Many2many(
        'fleet.vehicle.model.brand',
        'car_brand_mobile_partno_rel',  # Custom relation table name
        'partno_id',  # Column in the relation table referring to this model
        'brand_id',  # Column in the relation table referring to the 'car.brand' model
        string="Brand"
    )

    # Many2many relationship with car models
    model_ids = fields.Many2many(
        'fleet.vehicle.model',
        'fleet_vehicle_mobile_partno_rel',  # Different custom relation table name
        'partno_id',  # Column in the relation table referring to this model
        'model_id',  # Column in the relation table referring to the 'car.model' model
        string="Model"
    )

    @api.depends('partno_id')
    def _compute_partno_product_id(self):
        """Compute the related product.product for each part."""
        for record in self:
            if record.partno_id:
                record.partno_product_id = record.partno_id.product_variant_id

    @api.depends('partno', 'part_cat1.name', 'part_type')
    def _compute_formula_field(self):
        for record in self:
                
            part_number = record.partno or ''

            if len(part_number) >= 7:
                part_number = part_number[4:8]
            elif len(part_number) >= 4:
                part_number = part_number[4:]  # Get from index 4 to the end
            else:
                part_number = part_number.zfill(4)

            part_type_dict = dict(self.fields_get()['part_type']['selection'])
            main_category_code = record.part_cat1.name[:2] if record.part_cat1 else ''
            type_digit = part_type_dict.get(record.part_type, '') if record.part_type else ''

            seq = self.env['ir.sequence'].next_by_code('part.internal.no.sequence') or '0001'

            # Construct the formula
            record.part_internal_no = f"{part_number}{main_category_code}{type_digit}{seq}"

    year_ids = fields.Many2many(
        'year.selection',
        string="Years"
    )
    cost_price = fields.Float(string="Cost Price")
    sale_price = fields.Float(string="Sale Price")
    part_image = fields.Image(string="Image", max_width=824, max_height=824)

    @api.onchange('partno')
    def _onchange_part_nubmer_id(self):
        # Set the product_id based on the selected part number
        if self.partno:
            self.partno_id = self.partno_id
            self.partno_product_id = self.partno_product_id

        else:
            self.partno_id = False
            self.partno_product_id = False

    @api.onchange('cost_price')
    def _onchange_cost_price(self):
        for record in self:
            if record.cost_price:
                record.sale_price = record.cost_price * 1.25

    @api.constrains('sale_price', 'cost_price')
    def _check_sale_price(self):
        tolerance = 0.01  # Adjust tolerance as needed
        for record in self:
            if record.sale_price < (record.cost_price * 1.25) - tolerance:
                raise ValidationError(
                    "Sale price must be at least 25% higher than the cost price."
                )






# Model to manage year selection
class YearSelection(models.Model):
    _name = 'year.selection'
    _description = 'Year Selection'

    name = fields.Char(string='Year', required=True)
