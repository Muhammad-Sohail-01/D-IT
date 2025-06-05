# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class CarHistory(models.Model):
    _name = 'car.history'
    _description = 'Car Service History'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _rec_names_search = ['car_brand_id.name', 'plate_number']

    name = fields.Char(string='Number', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    car_brand_id = fields.Many2one('car.brand', 'Car Brand', required=True)
    car_model_id = fields.Many2one('car.model', 'Car Model')
    social_reference_id = fields.Many2one('car.social.reference', "Source")
    image_128 = fields.Binary(related='car_brand_id.image_128', readonly=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    year = fields.Char('Year')
    plate_number = fields.Char('Plate Number', required=True)
    vin_number = fields.Char('Vin Number', required=True)
    gear_type_id = fields.Many2one('car.gear.type', 'Transmission')
    color_id = fields.Many2one('car.color', 'Color', required=True)
    door = fields.Selection([('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('5+', '5+')], 'Number of Doors')
    spec_id = fields.Many2one('car.spec', 'Spec')
    cylinder_id = fields.Many2one('car.cylinder', 'Number of Cylinders')
    gear_box_id = fields.Many2one('car.gear.box', 'Gear Box')
    engine_cc = fields.Char('Engine CC')
    fuel_type = fields.Selection([('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                 'Fuel Type', default='electric')
    partner_id = fields.Many2one('res.partner', 'Customer')
    phone = fields.Char(related='partner_id.phone')

    # licence section
    licence_provider = fields.Selection([('uae', 'UAE'),
                                         ('qatar', 'Qatar'),
                                         ('kuwait', 'Kuwait'),
                                         ('bahrain', 'Bahrain'),
                                         ('oman', 'Oman'),
                                         ('saudi', 'Saudi Arabia'),
                                         ('other', 'Other')], string="Licence Provider")
    licence_number = fields.Char(string="Licence Number")
    licence_expire = fields.Date(string="Licence Expire")
    licence_image_front = fields.Binary(string="Licence Image Front")
    licence_image_back = fields.Binary(string="Licence Image Back")

    _sql_constraints = [
        ('vin_number_unique', 'unique (vin_number)', "The Badge ID must be unique, this one is already assigned to another employee."),
    ]

    #default context
    @api.model
    def default_get(self, fields_list):
        # Call super to get default values
        defaults = super(CarHistory, self).default_get(fields_list)
        # Check if context has 'default_partner_id'
        if self.env.context.get('default_partner_id'):
            defaults['partner_id'] = self.env.context.get('default_partner_id')
        return defaults



    # Constrain
    @api.constrains('vin_number')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_number and not len(record.vin_number) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.car_brand_id.name} [{account.plate_number}]"


    # Insurance_section
    def _get_insurance_tag_id(self):
        return self.env.ref('base.res_partner_category_insurance').id

    # Insurance_section
    insurance_provider = fields.Many2one('res.partner', string="Insurance",
                                         domain=[('category_id.name', '=', 'Insurance')]
                                         )
    insurance_number = fields.Char(string="Insurance Policy Number")
    insurance_expire = fields.Date(string="Insurance Expire")
    insurance_type = fields.Selection([('basic', 'Basic'),
                                       ('comprehensive', 'Comprehensive'),
                                       ('premium', 'Premium')], string="Insurance Type")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('car.history') or _('New')
        result = super(CarHistory, self).create(vals)
        return result

    def name_get(self):
        result = []
        for car_history in self:
            name = car_history.plate_number
            result.append((car_history.id, name))
        return result

    def create_inspection(self):
        sales_vals = {
            'partner_id': self.partner_id.id,
            'inspection_date': fields.Datetime.now(),
            'user_id': self.partner_id.user_id.id,
            'team_id': self.partner_id.team_id.id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'client_order_ref': self.partner_id.ref,
            'company_id': self.env.company.id,
            'state': 'draft',
            'car_history_id': self.id,
            'car_make': self.car_brand_id.id,
            'car_model': self.car_model_id.id,
            'year': self.year,
        }
        sales_id = self.env['sale.order'].create(sales_vals)

    def create_estimation(self):
        sales_vals = {
            'partner_id': self.partner_id.id,
            'date_order': fields.Datetime.now(),
            'user_id': self.partner_id.user_id.id,
            'team_id': self.partner_id.team_id.id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'client_order_ref': self.partner_id.ref,
            'company_id': self.env.company.id,
            'state': 'sale_create',
            'car_history_id': self.id,
            'car_make': self.car_brand_id.id,
            'car_model': self.car_model_id.id,
            'year': self.year,
        }
        sales_id = self.env['sale.order'].create(sales_vals)
        sales_id.action_confirm_sale_order()

    def create_invoice(self):
        invoice_vals = {
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Datetime.now(),
            'invoice_user_id': self.partner_id.user_id.id,
            'team_id': self.partner_id.team_id.id,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'ref': self.partner_id.ref,
            'company_id': self.partner_id.company_id.id or self.env.company.id,
            'state': 'draft',
            'car_history_id': self.id,
            'car_make': self.car_brand_id.id,
            'car_model': self.car_model_id.id,
            'year': self.year,
            'move_type': 'out_invoice',
        }
        invoice_id = self.env['account.move'].create(invoice_vals)
