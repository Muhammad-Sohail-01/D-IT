# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarCylinder(models.Model):
    _name = 'car.cylinder'
    _description = 'Car Cylinder'
    
    name = fields.Char('Number Of Cylinder')