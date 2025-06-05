# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    insurance_invoice = fields.Boolean(default=False, string="Insurance Invoice")
    insurance_company = fields.Many2one(comodel_name='res.partner',string="Insurance Company", domain="[('category_id.name', '=', 'Insurance')]", required=False)
    amount_nature = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
        ], default='fixed', store=True)
    receivable_insurance = fields.Float(string="Receivable Insurance",)
    receivable_insurance_fix = fields.Monetary(string="Receivable Insurance")
    insurance_amount_percentage =fields.Float(string="percentage", compute="_compute_insurance_amount")

    def _compute_insurance_amount(self):
        for record in self:
            total_price_subtotal = sum(
                line.price_subtotal for line in record.order_line)

            # Calculate the insurance amount based on the percentage value
            record.insurance_amount_percentage = (record.receivable_insurance / 100) * total_price_subtotal


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    insurance_company = fields.Many2one(comodel_name='res.partner', string="Insurance Company",
                                        domain="[('category_id.name', '=', 'Insurance')]")