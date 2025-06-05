# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarGearBox(models.Model):
    _name = 'car.gear.box'
    _description = 'Car Gear Box'
    
    name = fields.Char('Gear Box')