
from odoo import SUPERUSER_ID, _, api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    phone = fields.Char(related='partner_id.phone', store=True)
    car_history_id = fields.Many2one(related="sale_id.car_history_id", store=True)
    in_time = fields.Datetime(related="sale_id.in_time", store=True)
    out_time = fields.Datetime(related='sale_id.out_time', store=True)
    total_time = fields.Float(related='sale_id.total_time', store=True)
    current_mileage = fields.Char(related='sale_id.current_mileage', store=True)
    employee_id = fields.Many2one(related='sale_id.employee_id', store=True)
    service_writer_id = fields.Many2one(related='sale_id.service_writer_id', store=True)
    salesperson_id = fields.Many2one(related='sale_id.user_id', store=True)
    customer_trn = fields.Char(related='partner_id.vat', string="TRN", store=True)
    car_make = fields.Many2one(related="sale_id.car_make", store=True)
    car_model = fields.Many2one(related="sale_id.car_model", store=True)
    year = fields.Char(related="sale_id.year", store=True)
    plat_number = fields.Char(related="car_history_id.plate_number", store=True)
    source_id = fields.Many2one('utm.source', string="Source")


class StockMove(models.Model):
    _inherit = "stock.move"

    #sequence = fields.Integer(string='Sequence', default=10)
    #technician_id = fields.Many2one(related='sale_line_id.technician_id', string='Technician', store=True)
    description_picking = fields.Text(related='sale_line_id.name', string='Description of Picking', store=True)
    #service_type_id = fields.Many2one(related='sale_line_id.service_type_id', string="Service", store=True)
#     display_type = fields.Selection([
#         ('line_section', "Section"),
#         ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
