# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarSpec(models.Model):
    _name = 'car.spec'
    _description = 'Car Specification'
    
    name = fields.Char('Spec')