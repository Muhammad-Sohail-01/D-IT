# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deposit_default_product_id_insurance = fields.Many2one(
        related='company_id.sale_insurance_product_id',
        readonly=False,
        # previously config_parameter='sale.default_deposit_product_id',
    )