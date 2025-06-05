# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CarServiceReport(models.Model):
    _name = 'car.service.report'
    
    name = fields.Char('Invoice Number')
    plate_number = fields.Char('Plate Number', required=True)
    vin_number = fields.Char('Vin Number')
    inv_date = fields.Datetime(string='Invoice Date')
    car_model_id = fields.Many2one('car.model', 'Car Model')
    current_mileage = fields.Float('Current Mileage')
    issue_heading = fields.Text('Fault')
    warranty_details = fields.Text(string="Warranty Details")
    delivery_location = fields.Char('Delivery Location')
    partner_id = fields.Many2one('res.partner', 'Customer')

    def car_service_report_action(self):
        self.env['car.service.report'].search([]).unlink()
        car_service_ids = self.env['account.move'].search([])
        values_to_create = []
        for car_service in car_service_ids:
            if car_service.car_history_id:
                values_to_create.append({
                    'name': car_service.name,
                    'plate_number': car_service.car_history_id.plate_number,
                    'vin_number': car_service.car_history_id.vin_number,
                    'inv_date': car_service.invoice_date,
                    'car_model_id': car_service.car_history_id.car_model_id.id,
                    'current_mileage': car_service.current_mileage,
                    'issue_heading': car_service.issue_heading,
                    'warranty_details': car_service.warranty_details,
                    'delivery_location': car_service.delivery_location,
                    'partner_id': car_service.partner_id.id,
                    })
        if values_to_create:
            service_ids = self.env['car.service.report'].create(values_to_create)
        return {
            'name': 'Service Car',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'car.service.report',
            'target': 'current',
            'context': {
                'search_default_group_by_partner_id': 1,
                'group_by': 'partner_id',
            },
        }
