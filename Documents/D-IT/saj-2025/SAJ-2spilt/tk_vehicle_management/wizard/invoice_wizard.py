from odoo import fields, api, models


class VehicleInvoice(models.TransientModel):
    _name = 'vehicle.invoice'
    _description = 'Vehicle Invoice'

    inspection_id = fields.Many2one(comodel_name='vehicle.inspection', string="Job Card")
    invoice_id = fields.Many2one(comodel_name='account.move', string="Job Card Invoice")

    def print_invoice(self):
        # Include the selected invoice in the data parameter
        data = {'invoice_id': self.invoice_id.id,
                'inspection_id': self.inspection_id.id,
               }
        return self.env.ref('tk_vehicle_management.action_job_card_invoice_qweb_report').report_action(self, data=data)



    