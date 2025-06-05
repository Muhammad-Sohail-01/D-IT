from odoo import api, fields, models, _

class VehicleRequiredServicesInherit(models.Model):
    _inherit = 'vehicle.required.services'
    _description = 'Vehicle Required Services Inherit'

    estimate_time = fields.Float(string="Estimate Time", related="product_id.estimate_time")

    is_payment_verified = fields.Boolean(string="Is Payment Verified")


