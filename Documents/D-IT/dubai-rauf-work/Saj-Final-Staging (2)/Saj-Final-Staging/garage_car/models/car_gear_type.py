# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarGearType(models.Model):
    _name = 'car.gear.type'
    _description = 'Car Gear Types'
    
    name = fields.Char(string='Gear Type', required=True)