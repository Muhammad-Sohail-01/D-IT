from logging import Logger
from odoo import models, fields, api

class TimeOffPortal(models.Model):
    _name = 'time_off_portal.time_off_portal'
    _description = 'Time Off Request'
    _inherit = 'hr.leave'

    custom_field = fields.Char(string='Custom Field')