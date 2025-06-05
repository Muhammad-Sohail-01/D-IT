# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_discount = fields.Boolean(
        string="Allow Discount Over Limit",
        help="If it is True, discount Limit will not affect the user"
    )
    max_discount = fields.Float(
        string="Maximum Discount (%)",
        help="Maximum discount percentage allowed for this user"
    )

    approve_discount = fields.Boolean(
            string="Can Approve Discounts",
            help="If True, this user can approve discount requests."
    )