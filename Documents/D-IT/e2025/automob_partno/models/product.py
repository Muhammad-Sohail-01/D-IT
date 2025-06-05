# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partno_line_id = fields.One2many('auto.mobile.partno.line','partno_id')
    allowed_hour_change = fields.Boolean(string="Hours allowed change", default=True)


    def _update_estimate_time(self):
        """
        Synchronize the `estimate_time` field in related `product.product` records with the `product.template`.
        """
        for template in self:
            # Get all related products for the product template
            related_products = self.env['product.product'].search([('product_tmpl_id', '=', template.id)])
            
            # Update the estimate_time field for all related products
            for product in related_products:
                product.estimate_time = template.estimate_time

    def _update_partno_lines(self):
        if self.env.context.get('_syncing'):
            return
    
        for template in self:
            # Get all related products for the product template
            related_products = self.env['product.product'].search([('product_tmpl_id', '=', template.id)])
            
            for partno_line in template.partno_line_id:
                for product in related_products:
                    # Check if a corresponding entry already exists in auto.mobile.product.product.partno.line
                    existing_partno = self.env['auto.mobile.product.product.partno.line'].search([
                        ('partno_product_id', '=', product.id),
                        ('partno_id', '=', template.id),
                        ('partno', '=', partno_line.partno)
                    ], limit=1)
    
                    if existing_partno:
                        # Update the existing part line
                        existing_partno.write({
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
                        # Create a new part line for the product
                        self.env['auto.mobile.product.product.partno.line'].with_context(_syncing=True).create({
                            'partno': partno_line.partno,
                            'partno_id': template.id,
                            'partno_product_id': product.id,
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

    
        template._update_estimate_time()




    



