# -*- coding: utf-8 -*-
from google.auth import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class tk_management_ext(models.Model):
    _inherit = 'vehicle.health.report'
    _description = 'vehicle health Report Inherit'

    # leaders_ids = fields.Many2many('hr.employee', string="Team Leaders")

    # technician_ids = fields.Many2many('hr.employee', 'vhr_technician_rel', 'vhr_technician_id',
    #                                   'vhr_user_technician_id', string="Technicians",
    #                                   domain=[('technician', '=', True)])

    sale_person_id = fields.Many2one(related="inspection_id.sale_person_id", string="Receptionist",
                                     store=True)
    service_adviser_id = fields.Many2one(related="inspection_id.service_adviser_id",
                                         string="Service Advisor",
                                         store=True)