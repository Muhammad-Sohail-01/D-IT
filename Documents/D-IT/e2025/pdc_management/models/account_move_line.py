# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    pdc_id = fields.Many2one('pdc.wizard')
