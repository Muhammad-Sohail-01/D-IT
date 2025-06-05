# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class VehicleBayManagement(models.Model):
    _name = 'vehicle.bay'
    _description = 'vehicle Bay Management'

    name = fields.Char(string="Bay Name")
    bay_type = fields.Selection(
        [
            ('mechanicalworkshop', 'Mechanical Workshop'),
            ('washingbay', 'Washing Bay'),
            ('paintingroom', 'Painting Room'),
            ('dentingarea', 'Denting Area'),
            ('serviceexpress', 'Service Express'),
            ('electricalservicebay', 'Electrical Service Bay'),
            ('interiordetailingzone', 'Interior Detailing Zone'),
            ('suspensionandalignmentarea', 'Suspension and Alignment Area'),
            ('diagnosticslab', 'Diagnostics Lab'),
            ('custommodificationshop', 'Custom Modification Shop'),
            ('parkingarea', 'Parking Area')
        ],
        string='Bay Type'
    )
    car_count = fields.Integer(string="Car Count")
    bay_area_size = fields.Text(string="Bay Area Size(SQM)")
    company_id = fields.Many2one('res.company', string="Company")
