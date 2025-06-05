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
        res = super (SaleAdvancePaymentInv, self)._create_invoices (sale_orders)

        # Process each invoice created by the super method
        for invoice in res:
            # Ensure all the necessary accounts are properly set
            for line in invoice.invoice_line_ids:
                if line.product_id.is_warranty:
                    # Get accounts from product category
                    product_category = line.product_id.categ_id

                    # Set revenue account from product category
                    if product_category.property_account_income_categ_id:
                        line.account_id = product_category.property_account_income_categ_id.id

        return res

