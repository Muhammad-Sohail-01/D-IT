# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.tools import format_date, frozendict


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    _description = "Sales Advance Payment Invoice inherit"

    advance_payment_method = fields.Selection(
        selection_add=[
            ('insurance_customer', 'Insurance invoice (Customer)'),
            ('insurance_insurance', 'Insurance invoice (Insurance)'),
        ], ondelete={'insurance_insurance': 'set default', 'insurance_customer': 'set default'})

    insurance_amount = fields.Monetary(
        string="Insurance Amount",
        help="The percentage of amount to be invoiced in advance.", store=True)


    # insurance_amount_percentage = fields.Float(string="Amount", help="The fixed amount to be invoiced in advance.")

    @api.depends('company_id')
    def _compute_product_id(self):
        # Call the super method
        super(SaleAdvancePaymentInv, self)._compute_product_id()

        for wizard in self:
            wizard.product_id = False  # Reset product_id

            # Check if there is exactly one sale order
            if wizard.count == 1:
                # Determine the product ID based on the advance payment method
                if self.sale_order_ids.insurance_invoice:
                    # Set the product ID from the insurance product
                    wizard.product_id = wizard.company_id.sale_insurance_product_id
                else:
                    # Set the regular down payment product
                    wizard.product_id = wizard.company_id.sale_down_payment_product_id

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method(self):
        # Reset all order lines to not be insurance
        sale_order = self.sale_order_ids
        for line in self.sale_order_ids.order_line:
            line.is_insurance = False  # Reset to False first


        if self.advance_payment_method:
            # Set the related sale order lines as insurance
            for line in self.sale_order_ids.order_line:
                line.is_insurance = True  # Set to True for insurance lines

        if sale_order.amount_nature == 'fixed':
            self.insurance_amount = sale_order.receivable_insurance_fix
        elif sale_order.amount_nature == 'percentage':
            self.insurance_amount = sale_order.insurance_amount_percentage



            # Optionally print or log to verify
            for line in self.sale_order_ids.order_line:
                print(line.is_insurance)

    def _create_invoices(self, sale_orders):
        self.ensure_one()
        # Call the original method to keep existing functionality
        invoice = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)

        # Modify invoice lines if the advance_payment_method is 'insurance_insurance'
        if 'insurance_insurance' in self.advance_payment_method or 'insurance_customer' in self.advance_payment_method:

            for order in sale_orders:
                # Get the invoice lines related to this sale order

                invoice_lines = invoice.filtered(
                    lambda inv: any(line.sale_line_ids.order_id == order for line in inv.invoice_line_ids))
                for line in invoice_lines.invoice_line_ids:
                    # Update the line to use the insurance amount
                    line.price_unit = self.insurance_amount
                    line.price_subtotal = self.insurance_amount
                    line.price_total = self.insurance_amount  # Ensure total is updated

                # Set the partner ID on the invoice
                if invoice.partner_id:
                    invoice.partner_id = order.insurance_company

        return invoice


    def _prepare_down_payment_section_values(self, order):
        # Create a context if needed (not used in this snippet, but for reference)
        context = {'lang': order.partner_id.lang}
        name = super(SaleAdvancePaymentInv, self)._prepare_down_payment_section_values(order)

        sections = []  # Initialize the sections list
        insurance_section = None  # Initialize insurance_section
        # Check for down payment condition
        if self.advance_payment_method in ['fixed', 'percentage']:
            # Prepare the down payment section
            down_payment_section = {
                'name': _('Down Payments'),
                'product_uom_qty': 0.0,
                'order_id': order.id,
                'display_type': 'line_section',
                'is_downpayment': True,
                'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
            }
            sections.append(down_payment_section)
        # Check for insurance condition
        if self.advance_payment_method == ['insurance_insurance','insurance_customer']:
            insurance_section = {
                'name': _('Insurance'),
                'product_uom_qty': 0.0,
                'order_id': order.id,
                'display_type': 'line_section',
                'is_insurance': True,
                'sequence': order.order_line and order.order_line[-1].sequence + 2 or 15,
            }
            sections.append(insurance_section)  # Append only if insurance_section is defined

        return sections  # Return the list of sections

    def _get_down_payment_description(self, order):
        self.ensure_one()
        # Call the super method to retain any existing functionality
        name = super(SaleAdvancePaymentInv, self)._get_down_payment_description(order)

        # Customize the name based on the advance payment method
        if self.advance_payment_method == 'insurance_insurance':
            name = _("Insurance invoice (Insurance)")  # Note the correct string formatting
        elif self.advance_payment_method == 'insurance_customer':
            name = _("Insurance invoice (Customer)")

        return name



    def _prepare_base_downpayment_line_values(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}

        # Use the super method to get the default values
        so_values = super(SaleAdvancePaymentInv, self)._prepare_base_downpayment_line_values(order)

        # Modify the name for insurance payment types
        if self.advance_payment_method in ['insurance_insurance', 'insurance_customer']:
            so_values['name'] = _(
                'Insurance Payment: %(date)s (Draft)', date=format_date(self.env, fields.Date.today())
            )

        # Ensure other necessary fields are set, if needed
        so_values.update({
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'product_id': self.product_id.id,
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        })

        del context
        return so_values
