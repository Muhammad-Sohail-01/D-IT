# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_pack_ids = fields.Many2many(
        'product.product',
        'sale_order_product_pack_rel',
        string='Select Pack',
        domain=[('is_pack', '=', True)],
        help='The selected pack product for the sale order.'
    )

    @api.onchange('product_pack_ids')
    def onchange_product_pack_ids(self):
        if self.product_pack_ids:
            new_order_lines = []
            for rec in self.product_pack_ids:
                product_already_added = any(
                    line.product_id.id == rec._origin.id for line in
                    self.order_line)
                if not product_already_added:
                    new_order_lines.append((0, 0, {
                        'product_id': rec.id,
                        'name': rec.name,
                        'product_uom_qty': 1,
                        'price_unit': rec.pack_price,
                    }))
                    self.order_line = new_order_lines
        elif not self.product_pack_ids:
            self.order_line = [(5, 0, 0)]

    def action_confirm(self):
        super().action_confirm()
        for line in self.order_line:
            if line.product_id.is_pack:
                for record in line.product_id.pack_products_ids:
                    for rec in self.picking_ids:
                        move = rec.move_ids.create({
                            'name': record.product_id.name,
                            'product_id': record.product_id.id,
                            'product_uom_qty': record.quantity * line.product_uom_qty,
                            'product_uom': record.product_id.uom_id.id,
                            'picking_id': rec.id,
                            'location_id': rec.location_id.id,
                            'location_dest_id': rec.location_dest_id.id,
                        })
                        move._action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': 0 if self.product_id.is_pack == True else self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'sale_line_ids': [Command.link(self.id)],
            'is_downpayment': self.is_downpayment,
        }
        analytic_account_id = self.order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if 'analytic_distribution' in res:
                res['analytic_distribution'][analytic_account_id] = res[
                                                                        'analytic_distribution'].get(
                    analytic_account_id, 0) + 100
            else:
                res['analytic_distribution'] = {analytic_account_id: 100}
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res
