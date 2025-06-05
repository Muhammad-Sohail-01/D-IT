# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class purchase_ext(models.Model):
    _name = 'community.purchase'
    _description = 'purchase_ext.purchase_ext'

    name = fields.Many2one('hr.employee', help="You can find a participants by its Name.")
    object = fields.Char()
    vendor = fields.Many2one('res.partner', help="You can find a participants by its Name.")
    nature_of_purchase = fields.Many2one('product.product')
    attachments = fields.Binary()
    attachments_name = fields.Char()
    decision = fields.Selection([
        ('pending', 'Pending'),
        ('decision', 'Accepted'),
        ('rejected', 'Rejected')])
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company", )
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self._default_currency_id())
    amount = fields.Float()
    date = fields.Date()
    vendor_reference = fields.Char(string="Vendor Reference")
    approver_id = fields.Many2one('res.users', string="Approver")


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft')

    # def button_change_state_and_redirect(self):
    #     # Perform your logic to change state from 'draft' to 'warehouse'
    #     self.write({'state': 'confirm'})
    #     # main = self.env['ir.ui.menu'].search([('name', '=', 'Purchase Community')]).get_metadata()[0].get('id')
    #     # print(main)
    #


    def button_confirm(self):
        for rec in self:
            # Get the purchase amount
            purchase_amount = rec.amount

            # Get the setting amount from the configuration parameter and convert it to float
            setting_amount_str = rec.env['ir.config_parameter'].sudo().get_param('purchase_ext.amount', default='0')
            setting_amount = float(setting_amount_str)

            # Check if the purchase amount is greater than the setting amount
            if rec.amount >= setting_amount >= 20000:
                # Transition the record to the 'to approve' state
                rec.write({'state': 'to approve'})
            else:
                # Raise a warning if the purchase amount is less than the required minimum
                raise UserError("The purchase amount must be greater than or equal to $20,000.")

        return True



    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({'state': 'purchase', 'date': fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}



    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
            self.company_id.po_double_validation == 'one_step'
            or (self.company_id.po_double_validation == 'two_step'
                and self.amount_total < self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
            or self.user_has_groups('purchase.group_purchase_manager'))

    def button_cancel(self):
        for order in self:
            if order.decision not in ('rejected', 'pending'):
                raise UserError("Unable to cancel this purchase order. You must first reject the committee.")
        self.write({'state': 'cancel'})
        # main_menu_url = self.env.ref(main).id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': main_menu_url,
        #     'target': 'self',
        # }
        # main_menu_url = main
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': main_menu_url,
        #     'target': 'self',
        # }
        # Set the context to open the Kanban view after the action
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    def create_purchase_orders(self):
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        for record in self:
            vendor_id = record.vendor.id
            vendor_reference = record.vendor_reference

            # Create a purchase order
            purchase_order = PurchaseOrder.create({
                'partner_id': vendor_id,
                'partner_ref': vendor_reference,
                'state': 'draft',
                # Add other fields as needed
            })

            # Assuming you have a field 'product_id' in your module
            product_id = record.nature_of_purchase.id
            date = record.date
            amount = record.amount

            # Create a purchase order line
            purchase_order_line = PurchaseOrderLine.create({
                'order_id': purchase_order.id,
                'product_id': product_id,  # Use the ID of the product
                'date_planned': date,
                'price_subtotal': amount,
                # Add other required fields
                'name': 'Description of the product',
            })

            # Confirm the purchase order immediately after creation
            purchase_order.button_confirm()
            main_menu_id = self.env['ir.ui.menu'].search([('name', '=', 'Expression of Needs')]).get_metadata()[0].get(
                'id')

            main_menu_url = f'/web#view_type=list&model=community_purchase&menu_id={main_menu_id}'

            return {
                    'type': 'ir.actions.act_url',
                    'url': main_menu_url,
                    'target': 'self',
                }

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id
