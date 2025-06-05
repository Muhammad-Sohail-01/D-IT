# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    # @api.depends('order_line.working_hours')
    # def _compute_total_working_hours(self):
    #     """
    #     Compute the total hours of the SO.
    #     """
    #     for order in self:
    #         total_hours = 0.0
    #         for line in order.order_line:
    #             total_hours += line.working_hours
    #         order.update({
    #             'total_work_hours': total_hours,
    #         })

    #inherited fields from sale order object
    date_order = fields.Datetime(string='Order Date', 
                                 required=True, index=True, copy=False, 
                                 default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    state = fields.Selection([
        ('draft', 'Inspection'),
        ('sent', 'Estimate'),
        ('sale', 'Need to Invoice'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    #New created fields
    customer_trn = fields.Char(related='partner_id.vat', string="TRN", store=True)
    car_history_id = fields.Many2one('car.history', 'Service Car')
    car_make = fields.Many2one('car.brand', 'Car Make')
    car_model = fields.Many2one('car.model', 'Model')
    year = fields.Char('Year')
    in_time = fields.Datetime('In Time')
    out_time = fields.Datetime('Out Time')
    total_time = fields.Float('Total Time')
    current_mileage = fields.Char('Current Mileage')
    employee_id = fields.Many2one('hr.employee', 'Inspected By')
    service_writer_id = fields.Many2one('hr.employee', 'Technician')
    issue_heading = fields.Text('Customer Concerned')
    customer_note = fields.Text('Customer Note')
    attachment_ids = fields.Many2many('ir.attachment', 'sales_order_attachment_rel', 'sales_order_id',
                                      'attachment_id', 'Related Documents')
    image_one = fields.Image(max_width=128, max_height=128)
    image_two = fields.Image(max_width=128, max_height=128)
    image_three = fields.Image(max_width=128, max_height=128)
    image_four = fields.Image(max_width=128, max_height=128)
    image_five = fields.Image(max_width=128, max_height=128)
    image_six = fields.Image(max_width=128, max_height=128)
    phone = fields.Char(string="Phone")
    address_area = fields.Char(string="Address/Area")
    total_work_hours = fields.Float(string="Total Working Hours")
    ins_name = fields.Char(required=True, copy=False, states={'draft': [('readonly', False)]},
                           index=True, default=lambda self: _('New'))
    inspection_date = fields.Datetime(string="Inspection Date", default=fields.Datetime.now)

    

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.address_area = self.partner_id.address_area
            
    #values crud
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if order.partner_id:
                # Check if customer_phone or customer_address_area is being updated
                if 'phone' in vals:
                    order.partner_id.phone = vals['phone']
                if 'address_area' in vals:
                    order.partner_id.address_area = vals['address_area']
        return res
    
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['ins_name'] = self.env['ir.sequence'].next_by_code('sale.inspection', sequence_date=seq_date) or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)


        #values crud
        if self.partner_id:
            if 'phone' in vals:
                self.partner_id.phone = vals['phone']
            if 'address_area' in vals:
                self.partner_id.address_area = vals['address_area']
        
        result = super(SaleOrder, self).create(vals)
        return result

    # def action_confirm_sale_order(self):
    #     for order in self:
    #         if order.state != 'draft':
    #             raise UserError(_("You can only confirm orders in the 'Draft' state."))
    #         order.write(
    #             {
    #                 "name": self.env['ir.sequence'].next_by_code('sale.estimation') or _('New')
    #             }
    #         )
    #         order.write({'state': 'sale_create'})
        
    @api.onchange('in_time', 'out_time')
    def calculate_hours(self):
        if self.in_time and self.out_time:
            in_time = datetime.strptime(str(self.in_time), DEFAULT_SERVER_DATETIME_FORMAT)
            out_time = datetime.strptime(str(self.out_time), DEFAULT_SERVER_DATETIME_FORMAT)
            diff = out_time - in_time
            hours = (diff.seconds)/ 3600
            diff_days = diff.days
            days_hours = diff_days * 24
            total_hours = days_hours + hours
            self.total_time = total_hours

    @api.onchange('car_history_id')
    def onchange_car_history(self):
        if self.car_history_id:
            self.car_make = self.car_history_id.car_brand_id.id
            self.car_model = self.car_history_id.car_model_id.id
            self.year = self.car_history_id.year

    def _can_be_confirmed(self):
        super(SaleOrder, self)._can_be_confirmed()
        self.ensure_one()
        return self.state in {'draft', 'sent','sale_create'}
        

    

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     service_type_id = fields.Many2one('car.service.type', string="Service")
#     technician_id = fields.Many2one('hr.employee', 'Technician')
#     working_hours = fields.Float(string="Working Hours")
#
#     def _prepare_invoice_line(self, **optional_values):
#         res = super()._prepare_invoice_line(**optional_values)
#         if self.service_type_id:
#             res['service_type_id'] = self.service_type_id.id
#         return res
        
        
