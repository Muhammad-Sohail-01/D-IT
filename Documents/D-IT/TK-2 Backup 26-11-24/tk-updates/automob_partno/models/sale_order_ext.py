from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    part_nubmer_id = fields.Many2one('auto.mobile.partno.line', string="Part Number")
    part_internal_no = fields.Char(string="Internal No")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand", domain=[('part_no_id', '=', 'product_template_id')])
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    selected = fields.Boolean(string="Parts Selected")


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
    warranty_expiry_date = fields.Date(string="Warranty Expiry Date", compute="_compute_warranty_expiry_date", readonly=False, store=True)

    @api.depends('product_template_id')
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
        if not self.part_nubmer_id:
            return

        if self.part_nubmer_id.partno_id:
            self.product_template_id = self.part_nubmer_id.partno_id
            self.name = self.product_template_id.name
            self.product_uom = self.product_template_id.uom_id
            self.part_internal_no = self.part_nubmer_id.part_internal_no

            product_variants = self.product_template_id.product_variant_ids
            if product_variants:
                # Assuming you want to set the first available variant
                self.product_id = product_variants[0]

        # Check if the selected part number has a sale price
        if self.part_nubmer_id.sale_price:
            self.price_unit = self.part_nubmer_id.sale_price
        else:
        # Fallback to the list price if there's no sale price
            self.price_unit = self.product_template_id.list_price 

        
        

        # Display warning if there's a note
        if self.part_nubmer_id.note:
            return {
                'warning': {
                    'title': _("Warning for Part %s", self.part_nubmer_id.partno),
                    'message': self.part_nubmer_id.note,
                }
            }


    @api.onchange('product_template_id')
    def _onchange_product_id(self):
        """
        When `product_id` is changed, update the related `part_nubmer_id`.
        """
        if not self.product_template_id:
            self.part_nubmer_id = False
            self.part_internal_no = False
            return
    
        # Search for the part number related to the selected product
        part_number = self.env['auto.mobile.partno.line'].search([
            ('partno_id', '=', self.product_template_id.id)
        ], limit=1)
    
        if part_number:
            self.part_nubmer_id = part_number.id
            self.part_internal_no = part_number.part_internal_no
        else:
            self.part_nubmer_id = False
            self.part_internal_no = False

    @api.depends('product_template_id')
    def _compute_available_brand_ids(self):
        for line in self:
            if line.product_template_id:
                # Get all related brands from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search(
                    [('partno_id', '=', line.product_template_id.id)])
                brand_ids = partno_lines.mapped('brand_ids').ids
                line.available_brand_ids = [(6, 0, brand_ids)]
            else:
                line.available_brand_ids = [(6, 0, [])]

    @api.depends('product_template_id')
    def _compute_available_model_ids(self):
        for line in self:
            if line.product_template_id:
                # Get all related models from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search(
                    [('partno_id', '=', line.product_template_id.id)])
                model_ids = partno_lines.mapped('model_ids').ids
                line.available_model_ids = [(6, 0, model_ids)]
            else:
                line.available_model_ids = [(6, 0, [])]


    @api.model
    def write(self, vals):
        # Perform the regular write operation
        res = super(SaleOrderLine, self).write(vals)
        
        # Check if relevant fields have changed
        if any(field in vals for field in ['product_id', 'product_uom_qty', 'price_unit', 'tax_id']):
            # Call sync_vehicle_inspection on related orders
            self.mapped('order_id').sync_vehicle_inspection()
        
        return res














