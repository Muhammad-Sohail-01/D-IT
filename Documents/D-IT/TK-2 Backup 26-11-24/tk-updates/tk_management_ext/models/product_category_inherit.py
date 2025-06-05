from odoo import api, fields, models, _



class VehicleInspectionTaskInheritStage(models.Model):
    _inherit = 'product.category'


    def price_fixed(self):
        pass