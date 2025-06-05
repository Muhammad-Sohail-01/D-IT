from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    _description = "Sales Advance Payment Invoice inherit"

    

    def _create_invoices(self, sale_orders):
        self.ensure_one()
        # Call the original method to keep existing functionality
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
    
        for order in sale_orders:
            zero_price_lines = order.order_line.filtered(lambda line: line.price_unit == 0.0 and line.warranty_applicable)
    
            if len(zero_price_lines) >= 2:  # Ensure there are at least two zero-priced products with warranty_applicable = True
                # Get the configured journal from settings
                service_note_journal_id = self.env['ir.config_parameter'].sudo().get_param('tk_vehicle_management.service_note_journal_id')
                if service_note_journal_id:
                    # Assuming the stored value is a journal ID
                    journal = self.env['account.journal'].browse(int(service_note_journal_id))  # convert the string to an ID and fetch the journal
                    if journal:
                        for invoice in res:
                            # Set the journal to the fetched journal record
                            invoice.journal_id = journal
            else:
                # No zero-priced products with warranty_applicable = True, proceed with the regular flow
                for invoice in res:
                    # This would be your normal flow logic when no such lines exist
                    pass  # If nothing specific is needed, you can just leave it as `pass`
    
        return res
