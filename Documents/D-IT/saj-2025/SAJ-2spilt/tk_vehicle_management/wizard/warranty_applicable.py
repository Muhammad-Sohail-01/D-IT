from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    _description = "Sales Advance Payment Invoice inherit"

    def _create_invoices(self, sale_orders):
        self.ensure_one()
    
        all_invoices = self.env['account.move']
        for order in sale_orders:
            zero_price_lines = order.order_line.filtered(
                lambda line: line.price_unit == 0.0 and line.warranty_applicable
            )
            valued_lines = order.order_line.filtered(lambda line: line.price_unit > 0.0)
    
            if zero_price_lines and not valued_lines:
                service_note_journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    f'tk_vehicle_management.service_note_journal_id_{self.env.company.id}'
                )
    
                if not service_note_journal_id:
                    raise ValidationError(_("Service Note Journal is not configured in system settings."))
    
                journal = self.env['account.journal'].browse(int(service_note_journal_id))
                if not journal or journal.name != "Service Note" or journal.code != "SRN":
                    raise ValidationError(_("The journal must have the name 'Service Note' and code 'SRN'."))
    
                invoice = super(SaleAdvancePaymentInv, self)._create_invoices(order)
                invoice.write({'journal_id': journal.id})
            else:
                invoice = super(SaleAdvancePaymentInv, self)._create_invoices(order)
    
            # Find related vehicle inspection
            vehicle_inspection = self.env['vehicle.inspection'].search(
                [('sale_order_id', '=', order.id)], limit=1
            )
    
            if vehicle_inspection:
                invoice.job_card_id = vehicle_inspection.id  # Pass job card ID
                invoice.company_id = vehicle_inspection.company_id.id  # Pass company
                invoice.register_vehicle_id = vehicle_inspection.register_vehicle_id.id  # Pass vehicle
                
                # Link the invoice to the vehicle inspection
                vehicle_inspection.invoice_id = invoice.id  
    
            all_invoices += invoice
    
        return all_invoices




