import datetime
import operator
from collections import defaultdict
from odoo import models, api

class ReportCentralCash(models.AbstractModel):
    _name = 'report.tk_vehicle_management.job_card_invoice_report_template'
    _description = 'Central Cash Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data or 'invoice_id' not in data or 'inspection_id' not in data:
            raise UserError("Both Job Card and Invoice must be selected for printing.")

        # Fetch the specific invoice and inspection records
        inspection = self.env['vehicle.inspection'].browse(data['inspection_id'])
        invoice = self.env['account.move'].browse(data['invoice_id'])

        return {
            'doc_ids': [invoice.id],
            'doc_model': 'account.move',
            'docs': invoice,
            'inspection': inspection,  # Pass inspection separately
        }