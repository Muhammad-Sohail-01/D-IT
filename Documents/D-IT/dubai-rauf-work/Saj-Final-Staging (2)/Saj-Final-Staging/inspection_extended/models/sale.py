from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    other_salesperson_id = fields.Many2one(
        'hr.employee',
        string='Service Advisor',
        )

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'other_salesperson_id': self.other_salesperson_id.id, 
                    'car_history_id': self.car_history_id.id,
                    'car_in_time': self.in_time,
                    'car_out_time': self.out_time,
                    'total_time': self.total_time,
                    'current_mileage': self.current_mileage,
                    'employee_id': self.employee_id.id,
                    'service_writer_id': self.service_writer_id.id,
                    'issue_heading': self.issue_heading,
                    'customer_note': self.customer_note,
                    'customer_trn': self.partner_id.vat,
                    'car_make': self.car_history_id.car_brand_id.id,
                    'car_model': self.car_model.id,
                    'year': self.year,
                    'image_one': self.image_one,
                    'image_two': self.image_two,
                    'image_three': self.image_three,
                    'image_four': self.image_four,
                    'image_five': self.image_five,
                    'image_six': self.image_six,})
        return res


class AccountMove(models.Model):
    _inherit = "account.move"

    other_salesperson_id = fields.Many2one(
        'hr.employee',
        string='Service Advisor'
        )