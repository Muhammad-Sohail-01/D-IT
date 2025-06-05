import uuid
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehiclePartner(models.Model):
    _inherit = 'res.partner'

    address_area = fields.Char(string="Address/Area")