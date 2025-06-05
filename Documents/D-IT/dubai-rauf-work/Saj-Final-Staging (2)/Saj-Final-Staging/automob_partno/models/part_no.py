from odoo import models, fields, api
from datetime import datetime

# Model to manage part numbers
class PartNo(models.Model):
    _name = 'auto.mobile.partno.line'
    _description = 'Part No'
    _rec_name = 'partno'
    
    partno = fields.Char(string="Part No")
    partno_id = fields.Many2one('product.template', string="Product Template")
    
    # Many2many relationship with car brands
    brand_ids = fields.Many2many(
        'car.brand', 
        'car_brand_mobile_partno_rel',  # Custom relation table name
        'partno_id',  # Column in the relation table referring to this model
        'brand_id',  # Column in the relation table referring to the 'car.brand' model
        string="Brand"
    )
    
    # Many2many relationship with car models
    model_ids = fields.Many2many(
        'car.model', 
        'car_model_mobile_partno_rel',  # Different custom relation table name
        'partno_id',  # Column in the relation table referring to this model
        'model_id',  # Column in the relation table referring to the 'car.model' model
        string="Model"
    )
    
    # Many2many relationship with years
    year_ids = fields.Many2many(
        'year.selection',
        string="Years"
    )

# Model to manage year selection
class YearSelection(models.Model):
    _name = 'year.selection'
    _description = 'Year Selection'

    name = fields.Char(string='Year', required=True)

    
