# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super()._prepare_invoice_values(order, name, amount, so_line)
        if order.car_history_id:
            res['car_history_id'] = order.car_history_id.id
            res['car_in_time'] = order.in_time
            res['car_out_time'] = order.out_time
            res['total_time'] = order.total_time
            res['current_mileage'] = order.current_mileage
            res['employee_id'] = order.employee_id.id
            res['service_writer_id'] = order.service_writer_id.id
            res['issue_heading'] = order.issue_heading
            res['customer_note'] = order.customer_note
            res['customer_trn'] = order.partner_id.vat
            res['car_make'] = order.car_history_id.car_brand_id.id
            res['car_model'] = order.car_history_id.car_model_id.id
            res['year'] = order.car_history_id.year
        return res
