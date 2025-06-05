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



class WarrantyDuration(models.Model):
    _name = 'warranty.duration'
    _description = 'Warranty Durations'

    name = fields.Char(string='Name')
    duration_count = fields.Integer(string='Duration', default=1)
    unit = fields.Selection([('year', 'Year')], string='Unit', default='year')
