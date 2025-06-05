import uuid
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
import logging

_logger = logging.getLogger(__name__)

class VehicleWarranty(models.Model):
    _name = 'vehicle.warranty'
    _description = 'Vehicle Warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Fields
    name = fields.Char(
        string='Warranty No',
        readonly=True,
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    access_token = fields.Char(string="Access Token")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency'
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('expire', 'Expire'),
        ('cancel', 'Cancel')
    ], default='draft', tracking=True)

    # Customer Details
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner Detail",
        tracking=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string="Customer",
        tracking=True
    )
    email = fields.Char(
        string="Email",
        related="customer_id.email"
    )
    mobile = fields.Char(
        string="Mobile",
        related="customer_id.mobile"
    )

    # Vehicle Details
    register_vehicle_id = fields.Many2one(
        'register.vehicle',
        string="Register Vehicle",
        domain="[('customer_id','=',customer_id)]",
        tracking=True
    )
    brand_id = fields.Many2one(
        related="register_vehicle_id.brand_id",
        store=True
    )
    vehicle_model_id = fields.Many2one(
        related="register_vehicle_id.vehicle_model_id",
        store=True
    )
    registration_no = fields.Char(
        related="register_vehicle_id.registration_no",
        store=True
    )
    vin_no = fields.Char(
        related="register_vehicle_id.vin_no",
        store=True
    )
    year = fields.Char(
        related="register_vehicle_id.year",
        store=True
    )
    color = fields.Selection(
        related="register_vehicle_id.color",
        store=True
    )
    fuel_type = fields.Selection(
        related="register_vehicle_id.fuel_type",
        store=True
    )
    transmission = fields.Selection(
        related="register_vehicle_id.transmission",
        store=True
    )
    insurance_provider = fields.Many2one(
        'res.partner',
        related="register_vehicle_id.insurance_provider",
        store=True
    )
    milage = fields.Char(
        related="register_vehicle_id.milage",
        store=True
    )

    # Warranty Details
    warranty_product_id = fields.Many2one(
        'product.product',
        string="Warranty Product",
        tracking=True
    )

    start_date = fields.Date (
        string="Start Date",
        default=fields.Date.context_today,
        tracking=True
    )

    end_date = fields.Date (
        string="End Date",
        compute='_compute_end_date',
        store=True,
        readonly=True,
        tracking=True
    )

    duration = fields.Integer (
        string='Duration',
        tracking=True
    )

    period = fields.Selection ([
        ('1', 'Months'),
        ('12', 'Years')
    ], string='Period',
        default='12',
        tracking=True,
        help="Duration period: Months or Years"
    )

    next_reminder_date = fields.Date()
    price = fields.Monetary(string="Price")
    warranty_coverage = fields.Char(string="Coverage")
    warranty_limitation_ids = fields.Many2many(
        'warranty.attributes',
        'warranty_limitation_rel',
        'warranty_id',
        'attribute_id',
        string="Limitation"
    )
    warranty_description = fields.Html(string="Warranty Description")
    warranty_agreement = fields.Html(string="Warranty Agreement")
    terms_condition = fields.Html(string="Terms and Conditions")


    # Sale Order Related Fields
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        tracking=True
    )
    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice"
    )
    total_invoiced = fields.Monetary(
        related="invoice_id.amount_total",
        string="Invoice Amount"
    )

    @api.depends ('start_date', 'duration', 'period')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.duration and record.period:
                if record.period == '12':  # Years
                    record.end_date = record.start_date + relativedelta (years=record.duration)
                else:  # Months
                    record.end_date = record.start_date + relativedelta (months=record.duration)
            else:
                record.end_date = False

    @api.onchange ('start_date', 'duration', 'period')
    def _onchange_duration_period(self):
        if self.start_date and self.duration and self.period:
            if self.period == '12':  # Years
                self.end_date = self.start_date + relativedelta (years=self.duration)
            else:  # Months
                self.end_date = self.start_date + relativedelta (months=self.duration)

    @api.constrains ('duration')
    def _check_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError (_ ("Duration must be greater than 0."))


    # CRUD Methods
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
        for rec in self:
            if rec.status == 'running':
                raise UserError(_('You cannot delete running warranty.'))

    # Action Methods

    def action_cancel_vehicle_warranty(self):
        self.status = 'cancel'

    def action_reset_vehicle_warranty(self):
        self.status = 'draft'


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

    # Utility Methods
    def get_portal_url(self):
        url = "/my/vehicle/vehicle-warranty/form/" + self.access_token
        return url

    def create_recurring_entries(self):
        for warranty in self:
            if warranty.price <= 0:
                raise ValidationError (_ ("Warranty price must be greater than 0."))
            if not warranty.start_date or not warranty.end_date:
                raise ValidationError (_ ("Start Date and End Date must be defined."))

            # Get product category and validate accounts
            product_category = warranty.warranty_product_id.categ_id
            if not product_category:
                raise ValidationError (_ ("Product category is not set for warranty product."))

            # Validate accounts and journal
            deferred_revenue_account = product_category.deferred_revenue_account_id
            if not deferred_revenue_account:
                raise ValidationError (_ (
                    "Deferred Revenue Account is not configured for product category '%s'.",
                    product_category.name
                ))

            revenue_account = product_category.property_account_income_categ_id
            if not revenue_account:
                raise ValidationError (_ (
                    "Income Account is not configured for product category '%s'.",
                    product_category.name
                ))

            journal = product_category.deferred_journal_id
            if not journal:
                raise ValidationError (_ (
                    "Deferred Journal is not configured for product category '%s'.",
                    product_category.name
                ))

            # Calculate total days and daily price
            total_days = (fields.Date.from_string (warranty.end_date) -
                          fields.Date.from_string (warranty.start_date)).days + 1
            if total_days <= 0:
                raise ValidationError (_ ("End date must be after start date."))

            daily_price = warranty.price / total_days

            # Initialize date variables for monthly recognition
            current_date = fields.Date.from_string (warranty.start_date)
            end_date = fields.Date.from_string (warranty.end_date)

            # Track total amount recognized
            total_recognized = 0.0
            all_moves = self.env['account.move']

            # Create monthly revenue recognition entries
            while current_date <= end_date:
                # Calculate the last day of current month
                last_day_of_month = calendar.monthrange (current_date.year, current_date.month)[1]
                month_end_date = min (
                    current_date.replace (day=last_day_of_month),
                    end_date
                )

                # Calculate days and amount for current period
                days_in_period = (month_end_date - current_date).days + 1
                period_amount = days_in_period * daily_price

                # For all except the last period
                is_last_period = month_end_date == end_date
                if not is_last_period:
                    total_recognized += period_amount
                    amount_to_book = period_amount
                else:
                    # For the last period, adjust for any rounding differences
                    amount_to_book = warranty.price - total_recognized

                # Create JV entry for revenue recognition
                move = self.env['account.move'].create ({
                    'journal_id': journal.id,
                    'date': month_end_date,
                    'ref': f'Revenue Recognition - {warranty.name} - {month_end_date.strftime ("%B %Y")}',
                    'move_type': 'entry',
                    'line_ids': [
                        (0, 0, {
                            'name': 'Deferred Revenue Recognition',
                            'account_id': deferred_revenue_account.id,
                            'debit': amount_to_book,
                            'partner_id': warranty.customer_id.id,
                        }),
                        (0, 0, {
                            'name': 'Revenue Recognition',
                            'account_id': revenue_account.id,
                            'credit': amount_to_book,
                            'partner_id': warranty.customer_id.id,
                        })
                    ]
                })
                move._post ()
                all_moves += move

                # Move to next month
                current_date = month_end_date + relativedelta (days=1)

            # Validate total amount booked equals warranty price
            total_booked = sum (all_moves.mapped ('line_ids').filtered (lambda l: l.debit > 0).mapped ('debit'))
            if not float_utils.float_is_zero (total_booked - warranty.price, precision_digits=2):
                _logger.info (
                    'Warranty %s: Total booked (%.2f) differs from warranty price (%.2f). '
                    'Difference adjusted in last entry.',
                    warranty.name, total_booked, warranty.price
                )

            # Update warranty status
            warranty.write ({
                'status': 'running',
                'next_reminder_date': warranty.start_date + relativedelta (months=6)
            })



    # Scheduled Actions
    @api.model
    def expire_vehicle_warranty(self):
        today_date = fields.Date.today()
        warranty_rec = self.env['vehicle.warranty'].sudo().search([('status', '=', 'running')])
        for data in warranty_rec:
            if today_date >= data.end_date:
                data.status = 'expire'

    @api.model
    def action_send_warranty_checkup_reminder(self):
        today_date = fields.Date.today()
        warranty_records = self.env['vehicle.warranty'].search([('status', '=', 'running')])
        for rec in warranty_records:
            delta = relativedelta(rec.end_date, rec.start_date)
            if delta.months > 6 and rec.next_reminder_date and rec.next_reminder_date == today_date:
                mail_template = self.env.ref(
                    'tk_vehicle_management.vehicle_warranty_reminder_mail_template')
                if mail_template:
                    mail_template.send_mail(rec.id, force_send=True)
                    rec.next_reminder_date = today_date + relativedelta(months=6)


class WarrantyAttributes(models.Model):
    _name = 'warranty.attributes'
    _description = "Warranty Coverage"

    name = fields.Char(string="Title")


class WarrantySaleOrder(models.Model):
    _inherit = 'sale.order'

    is_any_warranty_product = fields.Boolean(
        string="Is any warranty product",  default=True,  
        compute="_compute_is_any_warranty_product"
    )
    warranty_count = fields.Integer(
        compute="_compute_warranty_count"
    )
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
                
                start_date = False if self.partner_sale_order else self.date_order.date()
                end_date = False if self.partner_sale_order else rec.warranty_expiry_date
                customer_id = False if self.partner_sale_order else self.partner_id.id
                partner_id = self.partner_id.id if self.partner_sale_order else False
    
                for quantity in range(int(rec.product_uom_qty)):
                    self.env['vehicle.warranty'].create({
                        'name': f"{self.name}-{quantity + 1}",
                        'company_id': self.env.company.id,
                        'customer_id': customer_id,
                        'partner_id': partner_id,
                        'warranty_product_id': rec.product_id.id,
                        'register_vehicle_id': self.register_vehicle_id.id,
                        'price': rec.price_total / rec.product_uom_qty,  
                        'duration': rec.product_template_id.duration,
                        'period': rec.product_template_id.period,
                        'start_date': start_date,
                        'end_date': end_date,
                        'sale_order_id': self.id,
                        'warranty_coverage': rec.product_template_id.warranty_coverage,
                        'warranty_limitation_ids': [(6, 0, rec.product_template_id.warranty_limitation_ids.ids)],
                        'warranty_description': rec.product_template_id.warranty_desc,
                        'status': 'draft',
                    })
    
        return res

    