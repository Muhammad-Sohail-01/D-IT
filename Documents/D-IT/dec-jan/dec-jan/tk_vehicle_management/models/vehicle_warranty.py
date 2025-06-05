import uuid
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class VehicleWarranty(models.Model):
    _name = 'vehicle.warranty'
    _description = 'Vehicle Warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    access_token = fields.Char(string="Access Token")
    name = fields.Char(string='Warranty No', readonly=True, default=lambda self: _('New'),
                       copy=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')
    status = fields.Selection([('draft', 'Draft'), ('running', 'Running'),
                               ('expire', 'Expire'), ('cancel', 'Cancel')],
                              default='draft', tracking=True)

    # Customer Details
    customer_id = fields.Many2one('res.partner', string="Customer")
    email = fields.Char(string="Email", related="customer_id.email")
    mobile = fields.Char(string="Mobile", related="customer_id.mobile")

    # Vehicle Details
    register_vehicle_id = fields.Many2one('register.vehicle', string="Register Vehicle",
                                          domain="[('customer_id','=',customer_id)]")
    brand_id = fields.Many2one(related="register_vehicle_id.brand_id", store=True)
    vehicle_model_id = fields.Many2one(related="register_vehicle_id.vehicle_model_id", store=True)
    registration_no = fields.Char(related="register_vehicle_id.registration_no", store=True)
    vin_no = fields.Char(related="register_vehicle_id.vin_no", store=True)
    year = fields.Char(related="register_vehicle_id.year", store=True)
    color = fields.Selection(related="register_vehicle_id.color", store=True)
    fuel_type = fields.Selection(related="register_vehicle_id.fuel_type", store=True)
    transmission = fields.Selection(related="register_vehicle_id.transmission", store=True)
    insurance_provider = fields.Many2one('res.partner', related="register_vehicle_id.insurance_provider", store=True)
     

    # Warranty Details
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    next_reminder_date = fields.Date()
    price = fields.Monetary(string="Price")
    # warranty_coverage_ids = fields.Many2many('warranty.attributes', string="Coverage")
    warranty_coverage = fields.Char(string="Coverage")
    warranty_limitation_ids = fields.Many2many('warranty.attributes', 'warranty_limitation_rel',
                                               'warranty_id',
                                               'attribute_id', string="Limitation")
    terms_condition = fields.Html(string="Terms and Conditions")
    warranty_description = fields.Html(string="Warranty Description")
    warranty_product_id = fields.Many2one('product.product', string="Warranty Product")

    # Duration
    # duration_id = fields.Many2one('warranty.duration', string="Duration")
    duration = fields.Integer(string='Duration')
    period = fields.Selection([('1', 'Months'), ('12', 'Years')], string='Number of Months ', default='12',
        help="The amount of time between two depreciations")

    # Sale Order Details
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    # DEPRECATED
    milage = fields.Char(related="register_vehicle_id.milage", store=True)
    warranty_agreement = fields.Html(string="Warranty Agreement")
    total_invoiced = fields.Monetary(related="invoice_id.amount_total", string="Invoice Amount")
    invoice_id = fields.Many2one('account.move', string="Invoice")

    # ORM : Create / Write / Constrain / Default_get
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.warranty') or _('New')
            vals['access_token'] = str(uuid.uuid4())
        res = super(VehicleWarranty, self).create(vals_list)
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_running_contract(self):
        """Unlink running warranty contract"""
        for rec in self:
            if rec.status == 'running':
                raise UserError(_('You cannot delete running warranty.'))

    @api.onchange('start_date', 'end_date')
    def _onchange_start_date(self):
        for rec in self:
            next_reminder_date = False
            if rec.start_date and rec.end_date:
                delta = relativedelta(rec.end_date, rec.start_date)
                if delta.months > 6:
                    next_reminder_date = rec.start_date + relativedelta(months=6)
            rec.next_reminder_date = next_reminder_date

    # @api.depends('duration_id', 'start_date', 'duration_id.duration_count')
    # def _compute_end_date(self):
    #     for rec in self:
    #         end_date = None
    #         if rec.duration_id and rec.start_date:
    #             end_date = rec.start_date + relativedelta(years=rec.duration_id.duration_count)
    #         rec.end_date = end_date

    # Button
    def action_running_vehicle_warranty(self):
        self.status = 'running'

    def action_cancel_vehicle_warranty(self):
        self.status = 'cancel'

    def action_reset_vehicle_warranty(self):
        self.status = 'draft'

    @api.model
    def expire_vehicle_warranty(self):
        today_date = fields.Date.today()
        warranty_rec = self.env['vehicle.warranty'].sudo().search([('status', '=', 'running')])
        for data in warranty_rec:
            if today_date >= data.end_date:
                data.status = 'expire'

    def action_view_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.sale_order_id.invoice_ids.ids)],
            'context': {'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def get_portal_url(self):
        url = "/my/vehicle/vehicle-warranty/form/" + self.access_token
        return url

    @api.model
    def action_send_warranty_checkup_reminder(self):
        today_date = fields.Date.today()
        # today_date = datetime.date(2025, 7, 1)
        warranty_records = self.env['vehicle.warranty'].search([('status', '=', 'running')])
        for rec in warranty_records:
            delta = relativedelta(rec.end_date, rec.start_date)
            if delta.months > 6 and rec.next_reminder_date and rec.next_reminder_date == today_date:
                mail_template = self.env.ref(
                    'tk_vehicle_management.vehicle_warranty_reminder_mail_template')
                if mail_template:
                    mail_template.send_mail(rec.id, force_send=True)
                    rec.next_reminder_date = today_date + relativedelta(months=6)


# Warranty Coverage
class WarrantyAttributes(models.Model):
    _name = 'warranty.attributes'
    _description = "Warranty Coverage"

    name = fields.Char(string="Title")


# Warranty Sale Order
class WarrantySaleOrder(models.Model):
    _inherit = 'sale.order'

    is_any_warranty_product = fields.Boolean(string="Is any warranty product",
                                             compute="_compute_is_any_warranty_product")
    warranty_count = fields.Integer(compute="_compute_warranty_count")
    job_card_id = fields.Many2one('vehicle.inspection')
    is_additional_part_service = fields.Boolean()

    @api.depends('order_line')
    def _compute_is_any_warranty_product(self):
        for rec in self:
            is_any_warranty_product = False
            product_warranty_products = rec.order_line.mapped('product_id').filtered(
                lambda product: product.is_warranty)
            if product_warranty_products:
                is_any_warranty_product = True
            rec.is_any_warranty_product = is_any_warranty_product

    def _compute_warranty_count(self):
        for rec in self:
            rec.warranty_count = self.env['vehicle.warranty'].search_count(
                [('sale_order_id', '=', rec.id)])

    def action_view_warranty(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warranties',
            'res_model': 'vehicle.warranty',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_confirm(self):
        res = super(WarrantySaleOrder, self).action_confirm()
        for order in self.picking_ids:
            order.job_card_id = self.job_card_id.id if self.job_card_id else False
            if self.is_additional_part_service:
                order.is_additional_part = True

        for rec in self.order_line:
            if rec.product_id.is_warranty:
                self.env['vehicle.warranty'].create({
                    'name': self.name,
                    'company_id': self.env.company.id,
                    'customer_id': self.partner_id.id,
                    'warranty_product_id': rec.product_id.id,
                    'register_vehicle_id': self.register_vehicle_id.id,
                    'price': rec.price_total,
                    'duration': rec.product_template_id.duration,
                    'period': rec.product_template_id.period,
                    'start_date': self.date_order.date(),
                    'end_date': rec.warranty_expiry_date,
                    'sale_order_id': self.id,
                    'warranty_coverage': rec.product_template_id.warranty_coverage,
                    'warranty_limitation_ids': [(6, 0, rec.product_template_id.warranty_limitation_ids.ids)],
                    'warranty_description': rec.product_template_id.warranty_desc,
                    'status': 'draft',
                })
                
        return res
