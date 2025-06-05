from odoo import fields, api, models


class VehicleProduct(models.Model):
    _inherit = 'product.product'

    estimate_time = fields.Float(string="Estimate Time")

    # Warranty
    is_warranty = fields.Boolean(string="Is Warranty")
    is_service_contract = fields.Boolean(string="Is Service Contract")
    # warranty_coverage_ids = fields.Many2many(comodel_name='warranty.attributes', string="Coverage")
    warranty_coverage = fields.Char(string="Coverage")
    warranty_limitation_ids = fields.Many2many(comodel_name='warranty.attributes',
                                               relation='product_warranty_limitation_rel',
                                               column1='warranty_id',
                                               column2='attribute_id',
                                               string="Limitation")
    warranty_desc = fields.Html(string="Warranty Description")
    duration_id = fields.Many2one(comodel_name='warranty.duration', string="warranty")
    duration = fields.Integer(string='Duration', help="The number of depreciations needed to depreciate your asset")
    period = fields.Selection([('1', 'Months'), ('12', 'Years')], string='Number of Months in a Period', default='12',
        help="The amount of time between two depreciations")
    per_hour_price = fields.Monetary(string="Per Hour Rate Amount", compute="_compute_hour_rate", store=True)
    allowed_hour_change = fields.Boolean(default=True, string="Hours allowed change")
    partner_sale_only = fields.Boolean (string="Partner Sale Only",
                                        help="If checked, this product can only be sold to partners")
    service_coverage = fields.Boolean (string="Service Coverage", tracking=True)
    service_coverage_km = fields.Float (string="Service Coverage (KM)", tracking=True)
    service_covered_products = fields.Many2many (
        'product.product',
        'template_service_covered_rel',
        'template_id',
        'covered_product_id',
        string="Covered Services",
        domain="[('type', '=', 'service')]"
    )
    service_product_quantities = fields.One2many (
        'product.service.quantity',
        'product_tmpl_id',
        string="Service Quantities"
    )


    interval_by_km = fields.Float(
        related='product_tmpl_id.interval_by_km',
        string='Warranty Interval (KM)',
        readonly=False,
        store=True
    )
    interval_by_month = fields.Integer(
        related='product_tmpl_id.interval_by_month',
        string='Warranty Interval (Months)',
        readonly=False,
        store=True
    )


    @api.depends('list_price', 'estimate_time')
    def _compute_hour_rate(self):
        for rec in self:
            if rec.estimate_time and rec.estimate_time > 0:
                hourly_rate = rec.list_price / rec.estimate_time
            else:
                hourly_rate = 0.0  # Default to 0 to avoid division by zero
            rec.per_hour_price = hourly_rate




class VehicleProductTemplate(models.Model):
    _inherit = 'product.template'

    estimate_time = fields.Float(string="Estimate Time")

    # Warranty
    is_warranty = fields.Boolean(string="Is Warranty")
    is_service_contract = fields.Boolean(string="Is Service Contract")
    # warranty_coverage_ids = fields.Many2many(comodel_name='warranty.attributes', string="Coverage")
    warranty_coverage = fields.Char(string="Coverage")
    warranty_limitation_ids = fields.Many2many(comodel_name='warranty.attributes',
                                               relation='product_tmpl_warranty_limitation_rel',
                                               column1='warranty_id',
                                               column2='attribute_id',
                                               string="Limitation")
    warranty_desc = fields.Html(string="Warranty Description")
    duration_id = fields.Many2one(comodel_name='warranty.duration', string="warranty")
    duration = fields.Integer(string='Duration', help="The number of depreciations needed to depreciate your asset")
    period = fields.Selection([('1', 'Months'), ('12', 'Years')], string='Number of Months in a Period', default='12',
        help="The amount of time between two depreciations")
    allowed_hour_change = fields.Boolean(string="Hours allowed change", default=True)
    partner_sale_only = fields.Boolean(string="Partner Sale Only",
                                        help="If checked, this product can only be sold to partners")
    service_coverage = fields.Boolean (string="Service Coverage", tracking=True)
    service_coverage_km = fields.Float (string="Service Coverage (KM)", tracking=True)
    service_covered_products = fields.Many2many(
        'product.product',
        'product_service_covered_rel',
        'product_id',
        'covered_product_id',
        string="Covered Services",
        domain="[('type', '=', 'service')]"
    )
    service_product_quantities = fields.One2many(
        'product.service.quantity',
        'product_id',
        string="Service Quantities"
    )

    interval_by_km = fields.Float (
        string='Warranty Interval (KM)',
        help='Maximum kilometers covered under warranty',
        default=0.0
    )
    interval_by_month = fields.Integer (
        string='Warranty Interval (Months)',
        help='Maximum months covered under warranty',
        default=0
    )

    @api.depends ('list_price', 'estimate_time')
    def _compute_hour_rate(self):
        for rec in self:
            if rec.estimate_time and rec.estimate_time > 0:
                hourly_rate = rec.list_price / rec.estimate_time
            else:
                hourly_rate = 0.0  # Default to 0 to avoid division by zero
            rec.per_hour_price = hourly_rate


class WarrantyDuration(models.Model):
    _name = 'warranty.duration'
    _description = 'Warranty Durations'

    name = fields.Char(string='Name')
    duration_count = fields.Integer(string='Duration', default=1)
    unit = fields.Selection([('year', 'Year')], string='Unit', default='year')


class ProductServiceQuantity(models.Model):
    _name = 'product.service.quantity'
    _description = 'Product Service Quantities'

    product_id = fields.Many2one('product.product', string="Product")
    product_tmpl_id = fields.Many2one('product.template', string="Product Template")
    service_product_id = fields.Many2one(
        'product.product',
        string="Service",
        domain="[('type', '=', 'service')]",
        required=True
    )
    quantity = fields.Integer(
        string="Allowed Quantity",
        default=-1,
        help="Set to -1 for unlimited quantity"
    )

