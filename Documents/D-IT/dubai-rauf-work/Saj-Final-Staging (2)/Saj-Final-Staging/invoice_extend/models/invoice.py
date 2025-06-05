# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _


class AccountMove(models.Model):
    _inherit = "account.move"
    
    warranty_details = fields.Text(string="Warranty Details")
    car_delivered = fields.Selection([('yes','Yes'),('no','No')], 'Car Delivered')
    delivery_location = fields.Char('Delivery Location')
    driver_details = fields.Char('Driver Details')
    out_time = fields.Datetime('Out Time')
    
    car_history_id = fields.Many2one('car.history', 'Service Car')
    car_in_time = fields.Datetime('In Time')
    car_out_time = fields.Datetime('Out Time')
    total_time = fields.Float('Total Time')
    current_mileage = fields.Char('Current Mileage')
    employee_id = fields.Many2one('hr.employee', 'Inspected By')
    service_writer_id = fields.Many2one('hr.employee', 'Technician')
    issue_heading = fields.Text('Issue fault Main heading')
    customer_note = fields.Text('Customer Note')
    customer_trn = fields.Char(string="TRN", store=True)
    car_make = fields.Many2one('car.brand', 'Car Make')
    car_model = fields.Many2one('car.model', 'Model')
    year = fields.Char('Year')
    
    image_one = fields.Image(max_width=128, max_height=128)
    image_two = fields.Image(max_width=128, max_height=128)
    image_three = fields.Image(max_width=128, max_height=128)
    image_four = fields.Image(max_width=128, max_height=128)
    image_five = fields.Image(max_width=128, max_height=128)
    image_six = fields.Image(max_width=128, max_height=128)
    phone = fields.Char(related='partner_id.phone')


    def set_amount_in_words(self, currency_id, amount):
        amount_in_words = currency_id.amount_to_text(amount) if currency_id else ''
        return amount_in_words
    
    def _get_name_invoice_report(self):
        self.ensure_one()
        return 'invoice_extend.report_invoice_document'
    
    def cutomer_amount_due(self, partner_id, move_type):
        amount_due = 0.0
        for res in self.env['account.move'].search([('partner_id','=',partner_id.id), ('move_type','=',move_type)]):
            amount_due += res.amount_residual
        return amount_due


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ref_number = fields.Char('Reference Number')
    car_service_id = fields.Many2one('car.history', string="Car Plate No.")
    # name = fields.Text(string='Label', tracking=True)
    #service_type_id = fields.Many2one('car.service.type', string="Service")
