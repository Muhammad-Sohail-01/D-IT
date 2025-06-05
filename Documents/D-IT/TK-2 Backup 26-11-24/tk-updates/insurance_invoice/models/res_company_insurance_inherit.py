# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'
    _check_company_auto = True

    sale_insurance_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Insurance Product",
        domain=[
            ('type', '=', 'service'),
            ('invoice_policy', '=', 'order'),
        ],
        help="Default product used for Insurance payments",
        check_company=True,
    )