# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarBrand(models.Model):
    _name = 'car.brand'
    _description = 'Brand of the Car'
    _order = 'name asc'
    
    name = fields.Char('Make', required=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
    model_count = fields.Integer(compute="_compute_model_count", string="", store=True)
    model_ids = fields.One2many('car.model', 'brand_id')
    active = fields.Boolean('Active', default=True)
    
    @api.depends('model_ids')
    def _compute_model_count(self):
        Model = self.env['car.model']
        for record in self:
            record.model_count = Model.search_count([('brand_id', '=', record.id)])

    def action_brand_model(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'car.model',
            'name': 'Models',
            'context': {'search_default_brand_id': self.id, 'default_brand_id': self.id}
        }
        return view
    
    
class CarModel(models.Model):
    _name = 'car.model'
    _description = 'Model of a Car'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    brand_id = fields.Many2one('car.brand', 'Manufacturer', required=True, help='Manufacturer of the Car')
    image_128 = fields.Image(related='brand_id.image_128', readonly=True)
    active = fields.Boolean('Active', default=True)
    
    image_one = fields.Image(max_width=128, max_height=128)
    image_two = fields.Image(max_width=128, max_height=128)
    image_three = fields.Image(max_width=128, max_height=128)
    image_four = fields.Image(max_width=128, max_height=128)
    image_five = fields.Image(max_width=128, max_height=128)
    image_six = fields.Image(max_width=128, max_height=128)
    
    attachment_ids = fields.Many2many('ir.attachment', 'car_model_attachment_rel', 'car_model_id',
                                      'attachment_id', 'Related Documents')
    
    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res
    
