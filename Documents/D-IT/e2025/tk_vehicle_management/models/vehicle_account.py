from odoo import fields, api, models


class VehicleAccount(models.Model):
    _inherit = 'account.move'

    job_card_id = fields.Many2one('vehicle.inspection', string="Job Card")
