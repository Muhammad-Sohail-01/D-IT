# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarSocialReference(models.Model):
    _name = 'car.social.reference'
    _description = 'Car Garage Reference'

    name = fields.Char(string='Reference', required=True)