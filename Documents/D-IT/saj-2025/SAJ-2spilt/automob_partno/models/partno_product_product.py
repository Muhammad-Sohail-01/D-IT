from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

from odoo.addons.base.models.ir_http import FasterRule

# Model to manage part numbers
class PartNoProductProduct(models.Model):
    _name = 'auto.mobile.product.product.partno.line'
    _description = 'Part No'
    _rec_name = 'partno'

    partno = fields.Char(string="Part No")
    partno_id = fields.Many2one('product.template', string="Product Template")
    partno_product_id = fields.Many2one('product.product', string="Product", store=True,)
    part_internal_no = fields.Char(string="Internal No", compute="_compute_formula_field", store=True)
    part_vendor_name = fields.Char(string="Vendor Name", store=True)
    part_type = fields.Selection(
        [('i', 'I'), ('o', 'O'), ('g', 'G'), ('h', 'H')],
        string='Type'
    )


    
    part_cat1 = fields.Many2many('item.catalog','item_catalog_product_rel', 'auto_mobile_partno_line_id', 'item_catalog_id', string="MAIN CATEGORY")
    part_cat2 = fields.Many2many('item.catalog', 'item_catalog_product2_rel','auto_mobile_partno_line_id','item_catalog_id', string="SUB CATEGORY")
    part_cat3 = fields.Many2many('item.catalog', 'item_catalog_product3_rel','auto_mobile_partno_line_id','item_catalog_id', string="PART ELEMENT")
    part_cat4 = fields.Many2many('item.catalog', 'item_catalog_product4_rel','auto_mobile_partno_line_id','item_catalog_id', string="CATALOG NAME")
    note = fields.Char(string="Note")

    brand_ids = fields.Many2many(
        'fleet.vehicle.model.brand',
        'car_brand_mobile_product_partno_rel',  # Custom relation table name
        'partno_product_id',  # Column in the relation table referring to this model
        'brand_id',  # Column in the relation table referring to the 'car.brand' model
        string="Brand"
    )

    # Many2many relationship with car models
    model_ids = fields.Many2many(
        'fleet.vehicle.model',
        'fleet_vehicle_mobile_product_partno_rel',  # Different custom relation table name
        'partno_product_id',  # Column in the relation table referring to this model
        'model_id',  # Column in the relation table referring to the 'car.model' model
        string="Model"
    )

    year_ids = fields.Many2many(
        'year.selection',
        string="Years"
    )
    cost_price = fields.Float(string="Cost Price", store=True)
    sale_price = fields.Float(string="Sale Price")
    part_image = fields.Image(string="Image", max_width=824, max_height=824)


    @api.depends('partno', 'part_internal_no', 'brand_ids.name')
    def _compute_display_name(self):
        for rec in self:
            # Safely handle multiple brands
            brand_names = ', '.join(rec.brand_ids.mapped('name')) if rec.brand_ids else ''
            rec.display_name = f"{rec.partno}/{rec.part_internal_no}[{brand_names}]"



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


    @api.onchange('cost_price')
    def _onchange_cost_price(self):
        for record in self:
            if record.cost_price:
                record.sale_price = record.cost_price * 1.25

    @api.constrains('sale_price', 'cost_price')
    def _check_sale_price(self):
        tolerance = 0.01  # Adjust this value as needed for your precision level
        for record in self:
            if record.sale_price < record.cost_price * 1.25 - tolerance:
                raise ValidationError("Sale price must be at least 25% higher than the cost price.")

