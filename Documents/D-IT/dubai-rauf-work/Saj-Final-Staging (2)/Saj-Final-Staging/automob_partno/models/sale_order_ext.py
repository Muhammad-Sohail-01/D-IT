from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    part_nubmer_id = fields.Many2one('auto.mobile.partno.line', string="Part Number")
    brand_id = fields.Many2one('car.brand', string="Brand", domain=[('part_no_id', '=', 'product_template_id')])
    model_id = fields.Many2one('car.model', string="Model")
    p_type = fields.Selection(
        [('i', 'I'), ('o', 'O'), ('g', 'G'), ('h', 'H')],
        string='Type'
    )

    available_brand_ids = fields.Many2many('car.brand', compute='_compute_available_brand_ids',
                                           string="Available Brands")
    available_model_ids = fields.Many2many('car.model', compute='_compute_available_model_ids',
                                           string="Available Models")
    
    is_warranty = fields.Boolean(string="Is Warranty", related='product_template_id.is_warranty', store=True)
    warranty_expiry_date = fields.Date(string="Warranty Expiry Date", compute='_compute_warranty_expiry_date', store=True)

    @api.depends('product_id')
    def _compute_warranty_expiry_date(self):
        for line in self:
            expiry_date = False
            product_template = line.product_id.product_tmpl_id  # Get the product template
            if product_template:
                duration = product_template.duration
                period = product_template.period
                if product_template.is_warranty:
                    if period == '12':  # Years
                        expiry_date = fields.Date.context_today(line) + relativedelta(years=duration)
                    elif period == '1':  # Months
                        expiry_date = fields.Date.context_today(line) + relativedelta(months=duration)
                        
            line.warranty_expiry_date = expiry_date
    

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

