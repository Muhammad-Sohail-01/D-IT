from odoo import SUPERUSER_ID, _, api, fields, models
from re import findall as regex_findall
from re import split as regex_split
from odoo.tools import float_round, float_is_zero
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class StockProductionLotInh(models.Model):
    _inherit = 'stock.lot'

    part_number_id = fields.Many2one(
        'auto.mobile.partno.line',
        string="Part Numbers"
    )

    part_internal_number = fields.Char(string="Internal No"
                                          )
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    part_vendor_name = fields.Char(related="part_number_id.part_vendor_name")
    part_type = fields.Selection(related="part_number_id.part_type")
    note = fields.Char(related="part_number_id.note")
    cost_price = fields.Float(related="part_number_id.cost_price", string="Cost Price")
    sale_price = fields.Float(related="part_number_id.sale_price", string="Sale Price")
    part_image = fields.Binary(related="part_number_id.part_image", string="Image")
    part_cat1 = fields.Many2many('item.catalog', related="part_number_id.part_cat1")
    part_main_category = fields.Char(string="Main Category", compute="_compute_main_cat")
    part_cat2 = fields.Many2many('item.catalog', related="part_number_id.part_cat2")
    sub_category = fields.Char(string="Sub Category", compute="_compute_sub_cat")
    part_cat3 = fields.Many2many('item.catalog', related="part_number_id.part_cat3")
    part_element = fields.Char(string="Part Element", compute="_compute_cat3")
    part_cat4 = fields.Many2many('item.catalog', related="part_number_id.part_cat4")
    catalog_name = fields.Char(string="Catalog Name", compute="_compute_cat4")
    
    

    


    year_ids = fields.Many2many(related="part_number_id.year_ids", string="Years")
    year_display = fields.Char(
        string="Year", compute="_compute_year_display", store=True
    )

    @api.depends('year_ids')
    def _compute_year_display(self):
        for record in self:
            # Get the names or display values of the related year_ids
            record.year_display = ", ".join(record.year_ids.mapped('name')) if record.year_ids else ''

    @api.depends('part_cat1')
    def _compute_main_cat(self):
        for cat1 in self:

            cat1.part_main_category = ", ".join(cat1.part_cat1.mapped('name')) if cat1.part_cat1 else ''

    @api.depends('part_cat2')
    def _compute_sub_cat(self):
        for cat2 in self:
            cat2.sub_category = ",".join(cat2.part_cat2.mapped('name')) if cat2.part_cat2 else ''

    @api.depends('part_cat3')
    def _compute_cat3(self):
        for cat3 in self:

            cat3.part_element = ", ".join(cat3.part_cat3.mapped('name')) if cat3.part_cat3 else ''

    @api.depends('part_cat4')
    def _compute_cat4(self):
        for cat4 in self:

            cat4.catalog_name = ", ".join(cat4.part_cat4.mapped('name')) if cat4.part_cat4 else ''

    
    



class StockMove(models.Model):
    _inherit = 'stock.move'

    part_number_id = fields.Many2one('auto.mobile.partno.line', string="Part Number",
                                     )  # Field to relate part numbers
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    part_internal_number = fields.Char(string="Internal No")
    cost_price = fields.Float(related="part_number_id.cost_price", string="Cost Price", readonly=False)
    sale_price = fields.Float(related="part_number_id.sale_price", string="Sale Price", readonly=False)
    
    

    # @api.onchange('part_number_ids')
    # def onchange_part_number_ids_method(self):
    #     if self.part_number_ids:
    #         products = self.env["product.product"].sudo().search([('part_number_ids', '=', self.part_number_ids.id)])
    #         return {'domain': {'product_id': [('id', 'in', products.ids)]}}

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals):
        records = super(StockMoveLine, self).create(vals)
    
        for record in records:
            # Check if the move line has a lot_id and a stock.move
            if record.lot_id and record.move_id:
                lot = record.lot_id
                move = record.move_id
                
                # Update the `stock.lot` fields based on `stock.move`
                lot.write({
                    'part_number_id': move.part_number_id.id if move.part_number_id else False,
                    'brand_id': move.brand_id.id if move.brand_id else False,
                    'model_id': move.model_id.id if move.model_id else False,
                    'part_internal_number': move.part_internal_number if move.part_internal_number else False,
                })
        
        return records



    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)

        for line in self:
            if 'lot_id' in vals and line.lot_id and line.move_id:
                lot = line.lot_id
                move = line.move_id
                
                # Update the `stock.lot` fields based on `stock.move`
                lot.write({
                    'part_number_id': move.part_number_id.id if move.part_number_id else False,
                    'brand_id': move.brand_id.id if move.brand_id else False,
                    'model_id': move.model_id.id if move.model_id else False,
                    'part_internal_number': move.part_internal_number if move.part_internal_number else False,
                })

        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # part_number_id = fields.Many2one('auto.mobile.partno.line', string="Parts Number")  
    #add parts detail to reciepts
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for move in res:
            move.update({'part_number_id': self.part_nubmer_id.id,
                        'brand_id': self.brand_id.id,
                        'model_id': self.model_id.id,
                        'part_internal_number': self.part_internal_no,})
        return res