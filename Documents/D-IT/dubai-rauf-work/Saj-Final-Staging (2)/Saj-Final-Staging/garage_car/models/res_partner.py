# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    car_line = fields.One2many('car.history', 'partner_id', 'Car Lines')
    

    def create_inspection(self):
        sales_vals = {
            'partner_id': self.id,
            'inspection_date': fields.Datetime.now(),
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'payment_term_id': self.property_payment_term_id.id,
            'fiscal_position_id': self.property_account_position_id.id,
            'client_order_ref': self.ref,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'draft',
            }
        sales_id = self.env['sale.order'].create(sales_vals)
        
    def create_estimation(self):
        sales_vals = {
            'partner_id': self.id,
            'date_order': fields.Datetime.now(),
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'payment_term_id': self.property_payment_term_id.id,
            'fiscal_position_id': self.property_account_position_id.id,
            'client_order_ref': self.ref,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'sale_create',
            }
        sales_id = self.env['sale.order'].create(sales_vals)
        sales_id.action_confirm_sale_order()

    def create_invoice(self):
        invoice_vals = {
            'partner_id': self.id,
            'invoice_date': fields.Datetime.now(),
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'invoice_payment_term_id': self.property_payment_term_id.id,
            'fiscal_position_id': self.property_account_position_id.id,
            'ref': self.ref,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'draft',
            'move_type': 'out_invoice',
            }
        invoice_id = self.env['account.move'].create(invoice_vals)
