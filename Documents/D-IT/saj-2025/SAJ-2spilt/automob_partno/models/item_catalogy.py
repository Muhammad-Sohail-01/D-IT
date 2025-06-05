from odoo import models, fields, api
from datetime import datetime


# Model to manage part numbers
class PartNo(models.Model):
    _name = 'item.catalog'
    _description = 'Catalog Category'
    _rec_name = 'name'

    name = fields.Char(string="Catalog Name")