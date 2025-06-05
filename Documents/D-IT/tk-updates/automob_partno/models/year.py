from odoo import models, fields, api
from datetime import datetime

class YearSelection(models.Model):
    _name = 'year.selection'
    _description = 'Year Selection'
    
    name = fields.Char(string="Year", required=True, unique=True, size=4)

    @api.model
    def create_years(self):
        for year in range(1900, 2051):
            self.create({'name': str(year)})