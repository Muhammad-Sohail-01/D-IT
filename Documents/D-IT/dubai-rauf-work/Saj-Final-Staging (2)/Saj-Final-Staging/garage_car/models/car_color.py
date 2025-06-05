# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarColor(models.Model):
    _name = 'car.color'
    _description = 'Car Color'

    name = fields.Char(string='Color', required=True)