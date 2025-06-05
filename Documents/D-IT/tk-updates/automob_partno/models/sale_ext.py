# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[

    ])
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('payment_verified', 'Prices verified'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')



    job_card_count = fields.Integer(compute="_compute_count")
    job_card_idd = fields.Many2one('vehicle.inspection')
    
    register_vehicle_id = fields.Many2one('register.vehicle', related="job_card_id.register_vehicle_id")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', related='job_card_id.brand_id')
    vehicle_model_id = fields.Many2one(related="job_card_id.vehicle_model_id", string="Model")
    vin_no = fields.Char(related="job_card_id.vin_no", string="VIN NO.")
    registration_no = fields.Char(related="job_card_id.registration_no", string="Registration No")
    year = fields.Char(related="job_card_id.year", string="Year")
    color = fields.Selection(related="job_card_id.color", string="Color")
    



    def _compute_count(self):
        for record in self:
            record.job_card_count = self.env['vehicle.inspection'].sudo().search_count(
                [('sale_order_id', '=', record.id)]
            )

    def action_redirect_to_job_card(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Jod Card',
            'res_model': 'vehicle.inspection',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }


    def _can_be_confirmed(self):
            self.ensure_one()
            return self.state in {'draft', 'sent','payment_verified'}

    def action_pay_verified(self):
        self.write({'state': 'payment_verified'})
        for order in self:
            if order.job_card_id:
                for line in order.order_line:
                # Check if the product is a service
                    if line.product_id.type == 'service':
                        for inspection in order.job_card_id.inspection_required_service_ids:
                            order.job_card_id.is_payment_verified = True
                            order.job_card_id.write({'is_payment_verified': True})
                            order.job_card_id.sale_order_id = self.id
                            if line.product_id.id == inspection.product_id.id:
                                inspection.price = line.price_unit
                                inspection.total_amount = line.price_unit

                    elif line.product_id.type == 'product':
                        for inspection_part in order.job_card_id.inspection_required_parts_ids:
                            if line.product_id.id == inspection_part.product_id.id:
                                inspection_part.price = line.price_unit
                                inspection_part.total_amount = line.price_unit
                order.job_card_id.write({'status': 'price_verified'})

    
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.id,  # assuming self is a recordset with the updated order
            'target': 'current',
            'context': {
                'message': _('Payment Verified!'),  # Pass message if needed
            },
        }


    # def action_confirm(self):
    #     # Call the original `action_confirm` method to proceed with confirmation.
    #     res = super(SaleOrder, self).action_confirm()

    #     # Check each sale order line to see if it has a product marked with `is_warranty=True`.
        
    #     return res

        

