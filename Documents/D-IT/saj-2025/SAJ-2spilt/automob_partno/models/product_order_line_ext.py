from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    part_nubmer_id = fields.Many2one('auto.mobile.product.product.partno.line', string="Part No")
    part_nubmer_id = fields.Many2one('auto.mobile.partno.line', string="Part Number", store=True)
    part_internal_no = fields.Char(string="Internal No")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand", domain=[('part_no_id', '=', 'product_id')])
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    p_type = fields.Selection(
        [('i', 'I'), ('o', 'O'), ('g', 'G'), ('h', 'H')],
        string='Type'
    )

    available_brand_ids = fields.Many2many(
    'fleet.vehicle.model.brand',
    'available_bra_rel',
    compute='_compute_available_brand_ids',
    string="Available Brands"
    )

    available_model_ids = fields.Many2many(
    'fleet.vehicle.model',
    'available_mod_rel',
    compute='_compute_available_model_ids',
    string="Available Models"
    )
    
    is_warranty = fields.Boolean(string="Is Warranty")
    warranty_expiry_date = fields.Date(string="Warranty Expiry Date", compute="_compute_warranty_expiry_date", store=True)

    @api.depends('is_warranty')
    def _compute_warranty_expiry_date(self):
        for line in self:
            expiry_date = False
            product_template = line.product_id  # Get the product template
            if product_template:
                duration = product_template.duration
                period = product_template.period
                if product_template.is_warranty:
                    if period == '12':  # Years
                        expiry_date = fields.Date.context_today(line) + relativedelta(years=duration)
                    elif period == '1':  # Months
                        expiry_date = fields.Date.context_today(line) + relativedelta(months=duration)
                        
            line.warranty_expiry_date = expiry_date

    @api.onchange('part_nubmer_id')
    def _onchange_part_nubmer_id(self):
        """
        When `part_nubmer_id` is changed, update the related `product_id` and other fields.
        """
        if not self.part_nubmer_id:
            self.product_id = False
            self.part_internal_no = False
            return
    
        # Set the product_id and other fields based on the selected part number
        self.product_id = self.part_nubmer_id.partno_product_id
        self.part_internal_no = self.part_nubmer_id.part_internal_no
        self.name = self.part_nubmer_id.part_vendor_name
        if self.part_nubmer_id.cost_price:
            self.price_unit = self.part_nubmer_id.cost_price
        else:
        # Fallback to the list price if there's no sale price
            self.price_unit = self.product_id.standard_price 


    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        When `product_id` is changed, update the related `part_nubmer_id`.
        """
        if not self.product_id:
            self.part_nubmer_id = False
            self.part_internal_no = False
            return
    
            # Display warning if there's a note
        if self.part_nubmer_id.note:
            return {
                'warning': {
                    'title': _("Warning for Part %s", self.part_nubmer_id.partno),
                    'message': self.part_nubmer_id.note,
                }
            }

    @api.depends('product_id')
    def _compute_available_brand_ids(self):
        for line in self:
            if line.product_id:
                # Get all related brands from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search(
                    [('partno', '=', line.part_nubmer_id.partno)])
                brand_ids = partno_lines.mapped('brand_ids').ids
                line.available_brand_ids = [(6, 0, brand_ids)]
            else:
                line.available_brand_ids = [(6, 0, [])]

    @api.depends('product_id')
    def _compute_available_model_ids(self):
        for line in self:
            if line.product_id:
                # Get all related models from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search(
                    [('partno', '=', line.part_nubmer_id.partno)])
                model_ids = partno_lines.mapped('model_ids').ids
                line.available_model_ids = [(6, 0, model_ids)]
            else:
                line.available_model_ids = [(6, 0, [])]



    # @api.model
    # def create(self, vals):
    #     """
    #     Ensure consistency when creating a record.
    #     """
    #     if 'part_nubmer_id' in vals:
    #         part = self.env['auto.mobile.product.product.partno.line'].browse(vals['part_nubmer_id'])
    #         vals.update({
    #             'product_id': part.partno_product_id.id,
    #             'part_internal_no': part.part_internal_no,
    #             'name': part.part_vendor_name,
    #             'price_unit': part.cost_price or part.partno_product_id.standard_price,
    #         })
    #     return super(PurchaseOrderLine, self).create(vals)

    # def write(self, vals):
    #     """
    #     Ensure consistency when writing a record.
    #     """
    #     if 'part_nubmer_id' in vals:
    #         part = self.env['auto.mobile.product.product.partno.line'].browse(vals['part_nubmer_id'])
    #         vals.update({
    #             'product_id': part.partno_product_id.id,
    #             'part_internal_no': part.part_internal_no,
    #             'name': part.part_vendor_name,
    #             'price_unit': part.cost_price or part.partno_product_id.standard_price,
    #         })
    #     return super(PurchaseOrderLine, self).write(vals)