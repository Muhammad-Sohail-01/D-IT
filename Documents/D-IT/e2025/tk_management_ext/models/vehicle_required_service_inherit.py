from odoo import api, fields, models, _

class VehicleRequiredServicesInherit(models.Model):
    _inherit = 'vehicle.required.services'
    _description = 'Vehicle Required Services Inherit'


    is_payment_verified = fields.Boolean(string="Is Payment Verified")


