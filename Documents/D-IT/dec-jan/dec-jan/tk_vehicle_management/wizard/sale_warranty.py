from odoo import api, fields, models, _


class SaleWarrantyWizard(models.TransientModel):
    _name = 'sale.warranty'
    _description = "Sale Warranty"

    sale_order_id = fields.Many2one('sale.order')
    customer_id = fields.Many2one('res.partner')
    register_vehicle_id = fields.Many2one('register.vehicle', string="Vehicle",
                                          domain="[('customer_id','=',customer_id)]")
    start_date = fields.Date(string="Start Date")

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(SaleWarrantyWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        sale_order_id = self.env['sale.order'].browse(active_id)
        res['sale_order_id'] = sale_order_id
        res['customer_id'] = sale_order_id.partner_id.id
        res['start_date'] = sale_order_id.date_order.date()
        return res

    def action_create_warranty_contract(self):
        for rec in self.sale_order_id.order_line:
            if rec.product_id.is_warranty:
                self.env['vehicle.warranty'].create({
                    'customer_id': self.customer_id.id,
                    'start_date': self.start_date,
                    'register_vehicle_id': self.register_vehicle_id.id,
                    'warranty_product_id': rec.product_id.id,
                    'price': rec.price_total,
                    'sale_order_id': self.sale_order_id.id,
                    'duration_id': rec.product_id.duration_id.id,
                    'warranty_coverage_ids': [(6, 0, rec.product_id.warranty_coverage_ids.ids)],
                    'warranty_limitation_ids': [(6, 0, rec.product_id.warranty_limitation_ids.ids)],
                    'warranty_description': rec.product_id.warranty_desc,
                })



class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        # Call the parent method with the necessary argument
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)

        # Get the order object (assuming it is passed in the sale_orders argument)
        order = sale_orders

        # Assuming the invoice is created and assigned after the parent method call
        # We should retrieve the invoice created
        for invoice in res:
            # Loop through order lines
            for order_line in order.order_line:
                # Check if the product has warranty
                if order_line.product_id.is_warranty:
                    # Loop through the invoice lines and match with order lines
                    for invoice_line in invoice.invoice_line_ids:
                        if invoice_line.product_id == order_line.product_id:
                            # Update the start and end dates for the warranty
                            invoice_line.write({
                                'deferred_start_date': order.date_order.date(),
                                'deferred_end_date': order_line.warranty_expiry_date,
                            })
        return res
