from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError



class PartNoProductPart(models.Model):
    _name = 'partno.sparepart'
    _description = 'Part No'
    _rec_name = 'product_id'


    product_id = fields.Many2one('product.product', string="Product")
    



    