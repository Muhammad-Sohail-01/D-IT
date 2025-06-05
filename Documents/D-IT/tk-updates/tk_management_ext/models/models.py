# -*- coding: utf-8 -*-
from google.auth import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class tk_management_ext(models.Model):
    _inherit = 'vehicle.inspection'
    _description = 'vehicle Inspection'
    _check_company_auto = False

    
    # service_adviser_id = fields.Many2one(
    #     comodel_name='hr.employee',
    #     string="Service Advisor",
    #     domain=lambda self: self._get_service_adviser_domain(),
    #     check_company=False
    # )

    
    # sale_person_id = fields.Many2one(
    #     'hr.employee',
    #     string="Receptionist",
    #     domain=[('receptionist', '=', True)],
    #     default=lambda self: self.env.user.employee_id if self.env.user else False

    # )

    status = fields.Selection(selection_add=[('price_verified', 'Price Verified'),('sent','Quotatoin Sent'),('concern',)]
                              , traking=True)

    is_payment_verified = fields.Boolean(
        string="Is Payment Verified")

    sale_order_id = fields.Many2one('sale.order', string="Reacted Sale Order")

    


    

    @api.constrains('miles')
    def _check_miles_value(self):
        if self.register_vehicle_id:  # Check if vehicle ID is registered
            if self.miles <= 1:
                raise ValidationError(_('Kilometers must be greater than 1.'))


class VehicleBookingInherit(models.Model):
    _inherit = 'vehicle.booking'
    _description = 'vehicle Booking'

    # sale_person_id = fields.Many2one(
    #     'hr.employee',
    #     string="Receptionist",
    #     domain=[('receptionist', '=', True)],
    #     default=lambda self: self.env.user.employee_id.id if self.env.user.employee_id else False
    # )

    # service_adviser_id = fields.Many2one('hr.employee', string="Service Advisor",
    #                                      domain=[('service_advisor', '=', True)],
    #                                      default=lambda
    #                                          self: self.env.user.employee_id.id if self.env.user.employee_id else False)
