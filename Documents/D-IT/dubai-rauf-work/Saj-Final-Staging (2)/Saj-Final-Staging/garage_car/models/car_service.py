# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarServiceType(models.Model):
    _name = 'car.service.type'
    _description = 'Car Service Type'
    
    name = fields.Char('Name')