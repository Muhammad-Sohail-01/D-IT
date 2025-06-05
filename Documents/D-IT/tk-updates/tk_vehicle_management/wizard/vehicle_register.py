from odoo import fields, api, models
from odoo.exceptions import ValidationError
import re


class VehicleRegister(models.TransientModel):
    """Vehicle Register"""
    _name = 'vehicle.register'
    _description = 'Vehicle Register'

    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Vehicle Brand")
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string="Model",
                                       domain="[('brand_id','=',brand_id)]")
    fuel_type = fields.Selection([('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                 'Fuel Type', default='electric')
    transmission = fields.Selection(
        [('manual', 'Manual'), ('automatic', 'Automatic'), ('cvt', 'CVT')],
        default='automatic')
    vin_no = fields.Char(string="VIN No.")
    registration_no = fields.Char(string="Registration No")
    miles = fields.Integer(string="Kilometers")
    year = fields.Char(string="Year")
    color = fields.Selection([
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('brown', 'Brown'),
        ('burgundy', 'Burgundy'),
        ('gold', 'Gold'),
        ('grey', 'Grey'),
        ('orange', 'Orange'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('silver', 'Silver'),
        ('beige', 'Beige'),
        ('tan', 'Tan'),
        ('teal', 'Teal'),
        ('white', 'White'),
        ('yellow', 'Yellow'),
        ('other', 'Other Color'),
    ], string="Color")
    is_warranty = fields.Boolean(string="Warranty")
    warranty_type = fields.Selection([('manufacture', 'Manufacture'),
                                      ('extended', 'Extended Warranty'),
                                      ('extended_evs', 'Extended With EVS')],
                                     string="Type of Warranty")
    insurance_provider = fields.Char(string="Insurance Provider")

    @api.constrains('year')
    def _check_year(self):
        for record in self:
            # Check if the input is a four-digit number between 1900 and 2200
            if not re.match(r'^(19[0-9]{2}|20[0-9]{2}|21[0-9]{2}|2200)$', record.year):
                raise ValidationError("Please enter a valid year between 1900 and 2200.")

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(VehicleRegister, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model and active_id:
            record_id = self.env[active_model].sudo().browse(active_id)
            res['brand_id'] = record_id.brand_id.id
            res['vehicle_model_id'] = record_id.vehicle_model_id.id
            res['fuel_type'] = record_id.fuel_type
            res['transmission'] = record_id.transmission
            res['vin_no'] = record_id.vin_no
            res['registration_no'] = record_id.registration_no
            res['miles'] = record_id.miles
            res['year'] = record_id.year
            res['color'] = record_id.color
            res['is_warranty'] = record_id.is_warranty
            res['warranty_type'] = record_id.warranty_type
            res['insurance_provider'] = record_id.insurance_provider
        return res

    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    def action_register_vehicle(self):
        """Register Vehicle"""
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        record_id = self.env[active_model].sudo().browse(active_id)
        register_vehicle_id = self.env['register.vehicle'].sudo().create({
            'customer_id': record_id.customer_id.id,
            'brand_id': self.brand_id.id,
            'vehicle_model_id': self.vehicle_model_id.id,
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'year': self.year,
            'color': self.color,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'insurance_provider': self.insurance_provider,
            'warranty_type': self.warranty_type,
            'is_warranty': self.is_warranty,
        })
        record_id.write({
            'register_vehicle_id': register_vehicle_id.id,
        })
        record_id.onchange_vehicle_info()
