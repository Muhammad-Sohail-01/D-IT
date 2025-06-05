# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    partno_line_id = fields.One2many(
    'auto.mobile.product.product.partno.line', 
    'partno_product_id', 
    readonly=False,  # Make it writable
    string="partno old line"
)
    partno_line_ids = fields.One2many('auto.mobile.partno.line','partno_product_id',
                                      compute='_compute_part_numbers', store=True)
    

    @api.depends('product_tmpl_id.partno_line_id')
    def _compute_part_numbers(self):
        """
        Computes part numbers for product variants based on the template.
        """
        for variant in self:
            variant.partno_line_ids = variant.product_tmpl_id.partno_line_id


    


    def _update_template_partno_lines(self):
        if self.env.context.get('_syncing'):
            return
    
        for product in self:
            template = product.product_tmpl_id
            if not template:
                continue
    
            for partno_line in product.partno_line_id:
                # Check if a corresponding entry exists in product.template's partno lines
                existing_template_partno = template.partno_line_id.filtered(lambda line: line.partno == partno_line.partno)
    
                if existing_template_partno:
                    # Update the existing part line in product.template
                    existing_template_partno.write({
                        'part_internal_no': partno_line.part_internal_no,
                        'part_vendor_name': partno_line.part_vendor_name,
                        'part_type': partno_line.part_type,
                        'part_cat1': [(6, 0, partno_line.part_cat1.ids)],
                        'part_cat2': [(6, 0, partno_line.part_cat2.ids)],
                        'part_cat3': [(6, 0, partno_line.part_cat3.ids)],
                        'part_cat4': [(6, 0, partno_line.part_cat4.ids)],
                        'cost_price': partno_line.cost_price,
                        'sale_price': partno_line.sale_price,
                        'note': partno_line.note,
                        'part_image': partno_line.part_image,
                        'brand_ids': [(6, 0, partno_line.brand_ids.ids)],
                        'model_ids': [(6, 0, partno_line.model_ids.ids)],
                    })
                else:
                    # Create a new part line in product.template
                    template.partno_line_id.with_context(_syncing=True).create({
                        'partno': partno_line.partno,
                        'partno_id': template.id,
                        'part_internal_no': partno_line.part_internal_no,
                        'part_vendor_name': partno_line.part_vendor_name,
                        'part_type': partno_line.part_type,
                        'part_cat1': [(6, 0, partno_line.part_cat1.ids)],
                        'part_cat2': [(6, 0, partno_line.part_cat2.ids)],
                        'part_cat3': [(6, 0, partno_line.part_cat3.ids)],
                        'part_cat4': [(6, 0, partno_line.part_cat4.ids)],
                        'cost_price': partno_line.cost_price,
                        'sale_price': partno_line.sale_price,
                        'note': partno_line.note,
                        'part_image': partno_line.part_image,
                        'brand_ids': [(6, 0, partno_line.brand_ids.ids)],
                        'model_ids': [(6, 0, partno_line.model_ids.ids)],
                    })


    @api.model_create_multi
    def create(self, vals):
        # Create the product.product record
        record = super(ProductProduct, self).create(vals)
        
        # Synchronize partno lines to product.template
        record._update_template_partno_lines()
        
        return record

    def write(self, vals):
        # Update the product.product record
        result = super(ProductProduct, self).write(vals)
        
        # Synchronize partno lines to product.template
        self._update_template_partno_lines()
        
        return result

