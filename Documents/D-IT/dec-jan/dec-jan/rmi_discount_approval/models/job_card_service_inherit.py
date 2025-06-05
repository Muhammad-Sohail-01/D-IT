from odoo import api, fields, models, _
from odoo.exceptions import ValidationError




class VehicleRequiredServices(models.Model):
    _inherit = 'vehicle.required.services'

    discount = fields.Float(string='Discount (%)', digits=0, default=0.0)

    

