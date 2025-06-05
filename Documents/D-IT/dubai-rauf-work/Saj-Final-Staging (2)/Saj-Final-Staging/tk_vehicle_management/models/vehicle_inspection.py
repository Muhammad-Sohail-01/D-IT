import uuid
from markupsafe import Markup
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleInspection(models.Model):
    _name = 'vehicle.inspection'
    _description = "Vehicle Job Card"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Job Card No', readonly=True, default=lambda self: _('New'), copy=False)
    access_token = fields.Char(string="Access Token")
    inspection_date = fields.Date(string="Date", default=fields.Date.today())
    status = fields.Selection([('draft', 'Draft'),
                               ('inspection_walkthrough', 'Walkaround Inspection'),
                               ('concern', 'Concern'),
                               ('concern_approve', 'Customer Approval'),
                               ('concern_reject', 'Concern Reject'),
                               ('quotation', 'Quotation'),
                               ('approve', 'Quotation Approved'),
                               ('reject', 'Quotation Rejected'),
                               ('parts_request', 'Spare Parts Request'),
                               ('parts_available', 'Spare Parts Available'),
                               ('in_repair', 'In Repair'),
                               ('ready_delivery', 'Ready for Delivery'),
                               ('complete', 'Complete'),
                               ('cancel', 'Cancel')], default="draft", tracking=True, group_expand='_expand_groups')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    update_quot_mail = fields.Boolean()

    # Booking Details
    booking_id = fields.Many2one('vehicle.booking', string="Check in No.")
    vehicle_from = fields.Selection([('new', "New"),
                                     ('customer_vehicle', "Vehicle From Customer")],
                                    string="Vehicle From", default='new')
    lead_id = fields.Many2one('crm.lead', string="Lead")
    booking_date = fields.Date(string="Check in Date", default=fields.Date.today)
    booking_source = fields.Many2one('car.history', string="Check in Source")
    other_source = fields.Char(string="Source")
    lead_source_id = fields.Many2one('utm.source', string="Lead Source")
    lead_medium_id = fields.Many2one('utm.medium', string="Lead Medium")

    # Customer Details
    customer_id = fields.Many2one('res.partner', string="Customer")
    last_name = fields.Char(string="Last Name")  # Deprecated
    email = fields.Char(string="Email", related="customer_id.email")
    phone = fields.Char(string="Phone", related="customer_id.phone")
    address_area = fields.Char(string="Address/Area")
    priority = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], string="Priority")
    customer_tag_ids = fields.Many2many('customer.tags', string="Tags")
    notes = fields.Html(string="Notes")
    business = fields.Boolean(string="Business")

    # Vehicle Details
    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    register_vehicle_id = fields.Many2one('register.vehicle', string="Register Vehicle",
                                          domain="[('customer_id','=',customer_id)]")
    brand_id = fields.Many2one('car.brand', string="Vehicle Brand")
    vehicle_model_id = fields.Many2one('car.model', string="Model")
                                       # domain="[('brand_id','=',brand_id)]"
    fuel_type = fields.Selection([('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                 'Fuel Type', default='electric')
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic'), ('cvt',          'CVT')],default='automatic')
    transmission_id = fields.Many2one('car.gear.type', string="Transmission")
    vin_no = fields.Char(string="VIN No.")
    registration_no = fields.Char(string="Registration No")
    miles = fields.Integer(string="Kilometers")
    year = fields.Char(string="Year")
    color = fields.Char(string="Color")
    is_warranty = fields.Boolean(string="Warranty")
    warranty_type = fields.Selection([('manufacture', 'Manufacture'),
                                      ('extended', 'Extended Warranty'),
                                      ('extended_evs', 'Extended With EVS')], string="Type of Warranty")
    insurance_provider = fields.Char(string="Insurance Provider")
    licence_image_front = fields.Image(string="Licence Image Front")
    licence_image_back = fields.Image(string="Licence Image Back")

    # Responsible
    sale_person_id = fields.Many2one('res.users', string="Receptionist",
                                     default=lambda self: self.env.user and self.env.user.id or False)
    service_adviser_id = fields.Many2one('res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])
    # Inspection Details
    inspect_type = fields.Selection([('only_inspection', "Only Inspection"),
                                     ('inspection_and_repair', "Inspection + Repair")], string="Inspection Type")
    inspection_type = fields.Selection([('full_inspection', "Full Inspection"),
                                        ('specific_inspection', "Specific Inspection")],
                                       default='full_inspection', string="Type of Inspection")

    # Customer Observation
    customer_observation = fields.Text(string="Customer Observation")

    # Images
    inner_image_ids = fields.One2many('inspection.inner.images', 'inspection_id', string="Inner Body Image")
    outer_image_ids = fields.One2many('inspection.outer.images', 'inspection_id', string="Outer Body Image")
    other_image_ids = fields.One2many('inspection.other.images', 'inspection_id', string="Other Image")

    # Check List
    checklist_template_id = fields.Many2one('checklist.template', string="Checklist Template")
    checklist_ids = fields.One2many('inspection.checklist', 'inspection_id')

    # Vehicle Health Report
    vehicle_health_report_id = fields.Many2one('vehicle.health.report')
    health_report_status = fields.Selection(related="vehicle_health_report_id.status", string="Inspection Status")
    inspection_required_service_ids = fields.One2many(
        related="vehicle_health_report_id.inspection_required_service_ids")
    inspection_required_parts_ids = fields.One2many(related="vehicle_health_report_id.inspection_required_parts_ids")
    # Service Total
    service_total = fields.Monetary(compute="_compute_total")
    estimate_time_total = fields.Float(compute="_compute_total")
    selected_services_time_total = fields.Float(compute="_compute_total")
    selected_services_total = fields.Monetary(compute="_compute_total")
    selected_services_untaxed = fields.Monetary(compute="_compute_total")
    selected_services_tax_amount = fields.Monetary(compute="_compute_total")
    # Parts Total
    parts_total = fields.Monetary(compute="_compute_total")
    additional_parts_total = fields.Monetary(compute="_compute_total")
    approved_part_amount = fields.Monetary(compute="_compute_total")
    report_additional_parts_total = fields.Monetary(compute="_compute_total")
    report_additional_part_final_total = fields.Monetary(compute="_compute_total")
    selected_parts_total = fields.Monetary(compute="_compute_total")
    selected_parts_untaxed = fields.Monetary(compute="_compute_total")
    selected_parts_tax_amount = fields.Monetary(compute="_compute_total")
    # Parts + Service - With Additional Part
    parts_total_qo_additional = fields.Monetary(compute="_compute_total")
    # Additional Part Total Amount
    additional_services_untaxed_total = fields.Monetary(compute="_compute_total")
    additional_parts_untaxed_total = fields.Monetary(compute="_compute_total")
    additional_parts_tax_amount = fields.Monetary(compute="_compute_total")
    additional_service_tax_amount = fields.Monetary(compute="_compute_total")
    # Inspection Final Total
    inspection_total = fields.Monetary(compute="_compute_total")
    # Shop Supply Fees
    shop_supplies_fees = fields.Monetary(compute="_compute_total")
    additional_shop_supplies_fees = fields.Monetary(compute="_compute_total")

    # Task
    task_ids = fields.One2many('project.task', 'inspection_id', string="Tasks")

    # Quality Check
    qc_check_ids = fields.One2many('inspection.qc.check', 'inspection_id', string="QC Check")
    qc_check_template_id = fields.Many2one(comodel_name='vehicle.qc.template')
    vehicle_qc_check_ids = fields.One2many(comodel_name='vehicle.quality.checks', inverse_name='inspection_id')

    # Quotation Details
    estimate_delivery_date = fields.Date(string="Estimate Delivery Date")

    # Count
    task_count = fields.Integer(string="Task Count", compute="_compute_task_count")
    delivery_order_count = fields.Integer(string="Delivery Order Count", compute="_compute_count")
    return_delivery_order_count = fields.Integer(string="Return Delivery Order Count", compute="_compute_count")
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_count")
    unselect_service_count = fields.Integer("Unselect Service Count", compute="_compute_count")
    unselect_part_count = fields.Integer("Unselect Part Count", compute="_compute_count")

    # Conditions
    task_check = fields.Boolean(string="Task Condition Check", compute="_compute_task_conditions")
    is_task_completed = fields.Boolean(compute="compute_task_completed")

    # Additional Part Delivery Order
    is_additional_part_order = fields.Boolean(compute="compute_any_additional_part_order")

    # Invoice
    invoice_id = fields.Many2one('account.move', string="Invoice")

    # Quotation Detail & Sign
    quot_reopen_request = fields.Selection([('draft', 'Draft'),
                                            ('reopen_expire', 'Re-open Expire'),
                                            ('reopen_reject', 'Re-open Reject'),
                                            ('reopen_cancel', 'Re-open Cancel')], default='draft')
    quote_url = fields.Char(string="Quotation URL", compute="compute_quotation_url")
    quote_state = fields.Selection([('draft', "Draft"),
                                    ('sent', "Sent"),
                                    ('signed', "Signed & Accepted"),
                                    ('reject', "Rejected"),
                                    ('expire', 'Expired'),
                                    ('cancel', "Cancelled")], string="Quotation Status", default='draft')
    is_expired = fields.Boolean(string="Is Quotation Expired")
    quotation_sent_date_time = fields.Datetime(string="Quotation Sent Date Time")
    quote_accept_date_time = fields.Datetime(string="Quotation Accepted Date Time")
    quote_expire_date = fields.Date(string="Quotation Expire Date", compute="compute_quot_expire_date")
    signature = fields.Image(string="Signature")
    quote_reject_reason = fields.Text(string="Quotation Reject Reason")
    service_selected = fields.Boolean(string="Service Selected")
    part_selected = fields.Boolean(string="Parts Selected")

    # Additional Parts Quotation
    additional_parts_quot_ids = fields.One2many('additional.part.confirmation', 'inspection_id')
    additional_part_quote_url = fields.Char(string="Additional Part Quotation URL",
                                            compute="compute_additional_part_quotation_url")
    additional_expiry_date = fields.Date(string="Additional Part Quotation Expire Date",
                                         compute="compute_additional_part_quotation_url")

    # Concern Sent Details & Sign
    customer_signature = fields.Binary(string="Customer Signature")
    authorized_signature = fields.Binary(string="Authorized Signature")
    vehicle_concern_ids = fields.One2many('inspection.concern', 'inspection_id')

    consent_access_token = fields.Char(string="Consent Access Token", readonly=True, store=True)
    consent_url = fields.Char(string="Consent URL", compute="compute_consent_url")
    consent_sent_state = fields.Selection([('draft', "Draft"),
                                           ('sent', "Sent"),
                                           ('signed', "Signed & Accepted"),
                                           ('reject', "Rejected"),
                                           ('expire', 'Expired'),
                                           ('cancel', "Cancelled")], string="Concern Status", default='draft')
    consent_reopen_request = fields.Selection([('draft', 'Draft'),
                                               ('reopen_expire', 'Re-open Expire'),
                                               ('reopen_reject', 'Re-open Reject')], default='draft')
    consent_is_expired = fields.Boolean(string="Is Consent Expired")
    consent_sent_date_time = fields.Datetime(string="Concern Sent Date Time")
    consent_accept_date_time = fields.Datetime(string="Concern Accepted Date Time")
    consent_expire_date = fields.Date(string="Concern Expire Date", compute="compute_consent_expiry_date")
    consent_reject_reason = fields.Text(string="Concern Reject Reason")

    # Warranty
    warranty_contract_id = fields.Many2one('vehicle.warranty', string="Warranty Contract")

    # Image Template
    image_template_id = fields.Many2one('job.image.template', string="Image Template")

    # DEPRECATED
    milage = fields.Char(string="Mileage")
    concern_template_id = fields.Many2one('vehicle.concern.template', string="Template")
    concern = fields.Html(string="Consent")
    job_card_concern_ids = fields.One2many(comodel_name='job.card.concern', inverse_name='inspection_id')
    quotation_amount = fields.Monetary(string="Quotation Amount")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'inspection_walkthrough', 'concern', 'concern_approve', 'concern_reject', 'quotation',
                'approve', 'reject', 'parts_request', 'parts_available', 'in_repair', 'ready_delivery', 'complete',
                'cancel']

    # ORM : Create / Write / Constrain / Default_get
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.inspection') or _('New')
            vals['access_token'] = str(uuid.uuid4())
        res = super(VehicleInspection, self).create(vals_list)
        return res

    # Constrain
    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    # Compute
    # Total Service and Parts
    @api.depends('inspection_required_service_ids', 'inspection_required_parts_ids')
    def _compute_total(self):
        for rec in self:
            # Service
            service_total = 0.0
            estimate_time_total = 0.0
            selected_services_time_total = 0.0
            selected_services_total = 0.0
            selected_services_untaxed = 0.0
            selected_services_tax_amount = 0.0
            # Parts
            parts_total = 0.0
            additional_parts_total = 0.0
            approved_part_amount = 0.0
            selected_parts_total = 0.0
            selected_parts_untaxed = 0.0
            selected_parts_tax_amount = 0.0

            # Additional Part & Services
            additional_services_untaxed_total = 0.0
            additional_parts_untaxed_total = 0.0
            additional_parts_tax_amount = 0.0
            additional_service_tax_amount = 0.0

            # Shop Supply Fees
            shop_supplies_fees = 0.0
            additional_shop_supplies_fees = 0.0

            # Services
            for s in rec.inspection_required_service_ids:
                service_total = service_total + s.total_amount
                estimate_time_total = estimate_time_total + s.estimate_time
                if s.service_selected:
                    selected_services_total = selected_services_total + s.total_amount
                    selected_services_untaxed = selected_services_untaxed + s.untaxed_amount
                    selected_services_tax_amount = selected_services_tax_amount + s.tax_amount
                    selected_services_time_total = selected_services_time_total + s.estimate_time
            # Parts
            for p in rec.inspection_required_parts_ids:
                parts_total = parts_total + p.total_amount
                if p.part_selected:
                    selected_parts_total = selected_parts_total + p.total_amount
                    selected_parts_untaxed = selected_parts_untaxed + p.untaxed_amount
                    selected_parts_tax_amount = selected_parts_tax_amount + p.tax_amount
                if p.is_additional_part:
                    if p.additional_part_status == 'pending':
                        additional_parts_total = additional_parts_total + p.total_amount
                    if p.additional_part_status == 'part_received':
                        approved_part_amount = approved_part_amount + p.total_amount

            # Additional Parts & Service
            additional_parts_list = rec.inspection_required_parts_ids.filtered(
                lambda line: line.is_additional_part and line.additional_part_status in ['pending',
                                                                                         'approve'])
            # Additional Services
            for service in additional_parts_list.mapped('service_id'):
                total_hours = sum(additional_parts_list.filtered(lambda line: line.service_id.id == service.id).mapped(
                    'required_time'))
                additional_services_untaxed_total = additional_services_untaxed_total + (service.price * total_hours)
                additional_service_tax_amount = additional_service_tax_amount + (
                    ((service.price * total_hours) * sum(service.tax_ids.mapped('amount')) / 100))

            # Additional Parts
            for part in additional_parts_list:
                additional_parts_untaxed_total = additional_parts_untaxed_total + part.untaxed_amount
                additional_parts_tax_amount = additional_parts_tax_amount + part.tax_amount

            # Shop Supplied Fees
            shop_supplies_fees_amount = (selected_services_untaxed * 2) / 100
            shop_supplies_fees = shop_supplies_fees_amount if shop_supplies_fees_amount <= 500 else 500

            # Additional Shop Supply Fees
            additional_shop_supplies_fees_amount = (additional_services_untaxed_total * 2) / 100
            additional_shop_supplies_fees = additional_shop_supplies_fees_amount if additional_shop_supplies_fees_amount <= 500 else 500

            # Service
            rec.service_total = service_total  # Not Selected Service Total Amount
            rec.estimate_time_total = estimate_time_total  # Not Selected Services
            rec.selected_services_time_total = selected_services_time_total  # Selected Service time Total
            rec.selected_services_tax_amount = selected_services_tax_amount  # Selected Service Tax Amount
            rec.selected_services_untaxed = selected_services_untaxed  # Selected Service untaxed Amount
            rec.selected_services_total = selected_services_total  # Selected Service Total Amount

            # Parts
            rec.parts_total = parts_total  # Not selected Part Total Amount
            rec.selected_parts_total = selected_parts_total  # Selected Parts Total Amount
            rec.approved_part_amount = approved_part_amount  # Additional Part Approved Total
            rec.additional_parts_total = additional_parts_total  # Pending Additional Part Total Amount
            rec.report_additional_parts_total = selected_parts_total + approved_part_amount
            rec.selected_parts_tax_amount = selected_parts_tax_amount  # Selected Part Tax Amount
            rec.selected_parts_untaxed = selected_parts_untaxed  # Selected Part untaxed Amount

            # Additional Part & Service
            rec.additional_services_untaxed_total = additional_services_untaxed_total
            rec.additional_parts_untaxed_total = additional_parts_untaxed_total
            rec.additional_parts_tax_amount = additional_parts_tax_amount
            rec.additional_service_tax_amount = additional_service_tax_amount

            # Shop Supplies Fees
            rec.shop_supplies_fees = shop_supplies_fees
            rec.additional_shop_supplies_fees = additional_shop_supplies_fees

            # Final Total
            rec.inspection_total = selected_services_total + selected_parts_total + approved_part_amount + shop_supplies_fees

            # DEPRECATED FIELDS
            report_additional_part_final_total = selected_services_total + selected_parts_total + approved_part_amount + additional_parts_total
            rec.report_additional_part_final_total = report_additional_part_final_total  #
            rec.parts_total_qo_additional = service_total + parts_total

    # Count
    def _compute_task_count(self):
        for rec in self:
            rec.task_count = self.env['project.task'].search_count([('inspection_id', '=', rec.id)])

    def _compute_count(self):
        for rec in self:
            rec.delivery_order_count = self.env['stock.picking'].search_count(
                [('job_card_id', '=', rec.id), ('picking_type_code', '=', 'outgoing')])
            rec.return_delivery_order_count = self.env['stock.picking'].search_count(
                [('job_card_id', '=', rec.id), ('picking_type_code', '=', 'incoming')])
            rec.invoice_count = self.env['account.move'].search_count([('job_card_id', '=', rec.id)])
            rec.unselect_service_count = self.env['vehicle.required.services'].sudo().search_count(
                [('vehicle_health_report_id', '=', rec.vehicle_health_report_id.id), ('active', '=', False),
                 ('display_type', '=', False), ('service_selected', '=', False)])
            rec.unselect_part_count = self.env['vehicle.required.parts'].sudo().search_count(
                [('vehicle_health_report_id', '=', rec.vehicle_health_report_id.id), ('active', '=', False),
                 ('display_type', '=', False), ('part_selected', '=', False)])

    # Conditions
    @api.depends('inspection_required_service_ids')
    def _compute_task_conditions(self):
        for rec in self:
            flag = True
            for data in rec.inspection_required_service_ids.filtered(lambda line: not line.display_type):
                if not data.task_id:
                    flag = False
                    break
            rec.task_check = flag

    @api.depends('inspection_required_parts_ids',
                 'inspection_required_parts_ids.is_additional_part',
                 'inspection_required_parts_ids.additional_part_status')
    def compute_any_additional_part_order(self):
        for rec in self:
            is_any_order = False
            for data in rec.inspection_required_parts_ids:
                if data.is_additional_part and data.additional_part_status == 'approve':
                    is_any_order = True
                    break
            rec.is_additional_part_order = is_any_order

    @api.depends('task_ids')
    def compute_task_completed(self):
        for rec in self:
            task_completed = True
            for data in rec.task_ids.filtered(lambda line: not line.is_inspection_task):
                if not data.task_state == 'complete':
                    task_completed = False
                    break
            rec.is_task_completed = task_completed

    # Quotation URL
    @api.depends('access_token')
    def compute_quotation_url(self):
        for rec in self:
            url = ""
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if rec.access_token and base_url:
                url = base_url + '/vehicle-service/job-card/' + rec.access_token
            rec.quote_url = url

    # Quotation Expire Date
    @api.depends('quotation_sent_date_time')
    def compute_quot_expire_date(self):
        for rec in self:
            date = False
            expire_config_days = self.env['ir.config_parameter'].sudo().get_param(
                'tk_vehicle_management.quot_expire_days')
            expire_days = int(expire_config_days) if expire_config_days else 7
            if rec.quotation_sent_date_time:
                date = rec.quotation_sent_date_time + relativedelta(days=expire_days)
            rec.quote_expire_date = date

    # Consent Expire Date
    @api.depends('consent_sent_date_time')
    def compute_consent_expiry_date(self):
        for rec in self:
            date = False
            expire_config_days = self.env['ir.config_parameter'].sudo().get_param(
                'tk_vehicle_management.consent_expire_days')
            expire_days = int(expire_config_days) if expire_config_days else 1
            if rec.consent_sent_date_time:
                date = rec.consent_sent_date_time + relativedelta(days=expire_days)
            rec.consent_expire_date = date

    # Consent URL
    @api.depends('consent_access_token')
    def compute_consent_url(self):
        for rec in self:
            url = ""
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if rec.consent_access_token and base_url:
                url = base_url + '/vehicle-service/consent-approval/' + rec.consent_access_token
            rec.consent_url = url

    # Additional Part Quotation URL
    @api.depends('additional_parts_quot_ids')
    def compute_additional_part_quotation_url(self):
        for rec in self:
            additional_part_record = self.env['additional.part.confirmation'].search(
                domain=[('inspection_id', '=', rec.id)],
                limit=1,
                order='id desc')
            url = ""
            expire_date = False
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if additional_part_record and rec.additional_parts_quot_ids:
                access_token = additional_part_record.access_token
                expire_date = additional_part_record.quote_expire_date
                url = base_url + '/vehicle-service/job-card/additional-part/' + access_token
            rec.additional_part_quote_url = url
            rec.additional_expiry_date = expire_date

    # Onchange
    # Customer Info
    @api.onchange('customer_id')
    def onchange_customer_info(self):
        for rec in self:
            rec.last_name = rec.customer_id.lastname
            rec.address_area = rec.customer_id.address_area

    # Vehicle Info
    @api.onchange('fleet_id', 'vehicle_from', 'register_vehicle_id')
    def onchange_vehicle_info(self):
        for rec in self:
            if rec.fleet_id and rec.vehicle_from == 'fleet_vehicle':
                rec.register_vehicle_id = False
                rec.brand_id = rec.fleet_id.model_id.brand_id.id
                rec.vehicle_model_id = rec.fleet_id.model_id.id
                rec.transmission = rec.fleet_id.transmission
                rec.registration_no = rec.fleet_id.license_plate
                rec.miles = rec.fleet_id.odometer if rec.fleet_id.odometer_unit == 'kilometers' else 0
                rec.year = rec.fleet_id.model_year
                rec.color = rec.fleet_id.color
            elif rec.register_vehicle_id and rec.vehicle_from == 'customer_vehicle':
                rec.fleet_id = False
                rec.brand_id = rec.register_vehicle_id.brand_id.id
                rec.vehicle_model_id = rec.register_vehicle_id.vehicle_model_id.id
                rec.transmission = rec.register_vehicle_id.transmission
                rec.registration_no = rec.register_vehicle_id.registration_no
                rec.vin_no = rec.register_vehicle_id.vin_no
                rec.year = rec.register_vehicle_id.year
                rec.color = rec.register_vehicle_id.color
                rec.fuel_type = rec.register_vehicle_id.fuel_type
                rec.is_warranty = rec.register_vehicle_id.is_warranty
                rec.insurance_provider = rec.register_vehicle_id.insurance_provider
                rec.warranty_type = rec.register_vehicle_id.warranty_type

    # Checklist Lines
    @api.onchange('checklist_template_id')
    def get_checklist_items(self):
        if self.checklist_template_id:
            checklist_items = [
                (0, 0, {
                    'name': item.name,
                    'display_type': item.display_type,
                    'sequence': item.sequence,
                })
                for item in self.checklist_template_id.template_line_ids.sorted('sequence')
            ]
            self.checklist_ids = [(5, 0, 0)]
            self.checklist_ids = checklist_items
        else:
            self.checklist_ids = [(5, 0, 0)]

    # Concern Template
    @api.onchange('concern_template_id')
    def get_concern_template(self):
        for rec in self:
            if rec.concern_template_id:
                rec.concern = rec.concern_template_id.concern

    # Vehicle Quality Check Template
    @api.onchange('qc_check_template_id')
    def _onchange_qc_check_template_id(self):
        for rec in self:
            lines = []
            rec.vehicle_qc_check_ids = [(5, 0, 0)]
            for data in rec.qc_check_template_id.template_line_ids:
                lines.append((0, 0, {
                    'name': data.name,
                    'sequence': data.sequence,
                    'display_type': data.display_type,
                }))
            rec.vehicle_qc_check_ids = lines

    # Vehicle Image Template
    @api.onchange('image_template_id')
    def onchange_image_template_id(self):
        for rec in self:
            rec.inner_image_ids = [(5, 0, 0)]
            rec.outer_image_ids = [(5, 0, 0)]
            rec.other_image_ids = [(5, 0, 0)]
            rec.inner_image_ids = [(0, 0, {'name': data.name}) for data in rec.image_template_id.inner_body_image_ids]
            rec.outer_image_ids = [(0, 0, {'name': data.name}) for data in rec.image_template_id.outer_body_image_ids]
            rec.other_image_ids = [(0, 0, {'name': data.name}) for data in rec.image_template_id.other_image_ids]

    # Button
    # Status Button
    def action_inspection_walkthrough(self):
        self.status = 'inspection_walkthrough'

    def action_status_quotation(self):
        self.quotation_sent_date_time = fields.Datetime.now()
        # Send Mail
        mail_template = self.env.ref('tk_vehicle_management.customer_inspection_quotation_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        # Send Whatsapp Message
        self.action_send_quot_whatsapp_message()
        self.quote_state = 'sent'
        self.status = 'quotation'

    def action_status_concern(self):
        wa_template_id = self.get_whatsapp_template(template_id='tk_vehicle_management.wa_consent_template_id')
        mobile_no = self.check_whatsapp_phone(self.customer_id)
        if not wa_template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Consent whatsapp template not found !'),
                    'message': _('Consent whatsapp template not configured. Please configured and Try Again.'),
                    'sticky': True,
                }}
        if not mobile_no:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Customer Mobile / Phone Missing !'),
                    'message': _('Customer Phone / Mobile is missing.'),
                    'sticky': True,
                }}

        self.consent_access_token = str(uuid.uuid4())
        self.consent_sent_date_time = fields.Datetime.now()
        self.consent_sent_state = 'sent'
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)
        self.status = 'concern'

    def action_status_concern_approve(self):
        self.status = 'concern_approve'

    def action_status_approve(self):
        if not self.quote_state == 'signed':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Customer Approval Pending !'),
                    'message': _(
                        'The customer has not yet approved the quotation. Once they do, you can proceed to approve it.'),
                    'sticky': False,
                }}
        self.status = 'approve'

    def action_status_reject(self):
        self.status = 'reject'

    def action_status_cancel(self):
        delivery_orders = self.env['stock.picking'].sudo().search([('job_card_id', '=', self.id)])
        return_order_ids = []
        if delivery_orders:
            for rec in delivery_orders:
                if rec.state in ['draft', 'assigned', 'confirmed', 'waiting']:
                    rec.action_cancel()
                if rec.state == 'done':
                    return_id = self.env['stock.return.picking'].sudo().create({
                        'picking_id': rec.id
                    })
                    return_id._create_returns()
                    return_order_ids.append(rec.id)
        self.status = 'cancel'

    def action_status_reset_draft(self):
        self.status = 'draft'

    def action_skip_spare_part(self):
        self.status = 'parts_available'

    def action_inspection_ready_delivery(self):
        self.send_whatsapp_qc_checks()
        self.status = 'ready_delivery'

    def action_complete_job_card(self):
        self.status = 'complete'

    def action_parts_available_received(self):
        delivery_orders = self.env['stock.picking'].search([('job_card_id', '=', self.id)])
        pending_delivery = False
        for data in delivery_orders:
            if not data.state == 'done':
                pending_delivery = True
        if pending_delivery:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Pending Delivery Orders !'),
                    'message': _('Please complete pending delivery orders to receive parts.'),
                    'sticky': False,
                }}
        self.status = 'parts_available'

    def action_create_additional_delivery_order(self):
        warehouse_id = self.company_id.part_warehouse_id
        if not warehouse_id:
            message = _(
                'Company Parts warehouse is not set. Please set the warehouse and try again. Goto Companies > Part Warehouse')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warehouse Missing !'),
                    'message': message,
                    'sticky': False,
                }}
        lines = []
        approved_parts = self.inspection_required_parts_ids.filtered(
            lambda line: line.is_additional_part == True and line.additional_part_status == 'approve')
        total_required_parts = approved_parts.mapped('id')
        for data in approved_parts:
            lines.append((0, 0, {
                'product_id': data.product_id.id,
                'product_uom_qty': data.qty,
                'product_uom': data.uom_id.id,
                'location_id': warehouse_id.lot_stock_id.id,
                'location_dest_id': warehouse_id.wh_output_stock_loc_id.id,
                'name': data.name,
                'additional_part_id': data.id
            }))
            data.additional_part_status = 'part_request'
        stock_picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse_id.id)], limit=1)
        if lines and stock_picking_type_id:
            delivery_order_id = self.env['stock.picking'].create({
                'partner_id': self.customer_id.id,
                'picking_type_id': stock_picking_type_id.id,
                'location_id': warehouse_id.lot_stock_id.id,
                'location_dest_id': warehouse_id.wh_output_stock_loc_id.id,
                'move_ids_without_package': lines,
                'move_type': 'one',
                'job_card_id': self.id,
                'is_additional_part': True,
                'additional_part_ids': [(6, 0, total_required_parts)]
            })

    def action_request_spare_part(self):
        warehouse_id = self.company_id.part_warehouse_id
        if not warehouse_id:
            message = _(
                'Company Parts warehouse is not set. Please set the warehouse and try again. Goto Companies > Part Warehouse')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warehouse Missing !'),
                    'message': message,
                    'sticky': False,
                }}
        lines = []
        for data in self.inspection_required_parts_ids.filtered(
                lambda line: not line.is_additional_part and not line.display_type):
            lines.append((0, 0, {
                'product_id': data.product_id.id,
                'product_uom_qty': data.qty,
                'product_uom': data.uom_id.id,
                'location_id': warehouse_id.lot_stock_id.id,
                'location_dest_id': warehouse_id.wh_output_stock_loc_id.id,
                'name': data.name
            }))
        stock_picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse_id.id)], limit=1)
        if lines and stock_picking_type_id:
            delivery_order_id = self.env['stock.picking'].create({
                'partner_id': self.customer_id.id,
                'picking_type_id': stock_picking_type_id.id,
                'location_id': warehouse_id.lot_stock_id.id,
                'location_dest_id': warehouse_id.wh_output_stock_loc_id.id,
                'move_ids_without_package': lines,
                'move_type': 'one',
                'job_card_id': self.id,
            })
            self.status = 'parts_request'

    def action_create_invoice(self):
        invoice_term = self.env.ref('tk_vehicle_management.term_condition_1').terms_conditions if self.env.ref(
            'tk_vehicle_management.term_condition_1') else False
        shop_supply_product_id = self.env['ir.config_parameter'].sudo().get_param(
            'tk_vehicle_management.shop_supply_product_id')
        if not shop_supply_product_id:
            message = _(
                'Shop Supplies and Environmental Fees Product is not set please configure. Goto Configuration > Shop Supplies and Environmental Fees')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Shop Supplies and Environmental Product Missing !'),
                    'message': message,
                    'sticky': False,
                }}
        lines = []
        if self.inspection_required_service_ids:
            lines = lines + [(0, 0, {'display_type': 'line_section', 'name': 'Services'})] + self.prepare_invoice_line(
                self.inspection_required_service_ids.filtered(lambda line: not line.display_type), 'services')
        if shop_supply_product_id:
            lines = lines + [
                (0, 0, {'display_type': 'line_section', 'name': 'Shop Supplies and Environmental Fees'})] + [
                        (0, 0, {'product_id': int(shop_supply_product_id),
                                'name': 'Shop Supplies and Environmental Fees',
                                'quantity': 1,
                                'price_unit': self.shop_supplies_fees,
                                'tax_ids': False
                                })]
        if self.inspection_required_parts_ids:
            # Default Part Line
            default_part_line = self.inspection_required_parts_ids.filtered(
                lambda line: not line.is_additional_part and not line.display_type)
            lines = lines + [(0, 0, {'display_type': 'line_section', 'name': 'Parts'})] + self.prepare_invoice_line(
                default_part_line, 'default_product')
            # Additional Parts
            additional_part_line = self.inspection_required_parts_ids.filtered(
                lambda
                    line: line.is_additional_part and line.additional_part_status == 'part_received' and not line.display_type)
            lines = (lines + [(0, 0, {'display_type': 'line_section', 'name': 'Additional Parts'})] +
                     self.prepare_invoice_line(additional_part_line, 'additional_product'))
        invoice_id = self.env['account.move'].create({
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'job_card_id': self.id,
            'invoice_line_ids': lines,
            'narration': invoice_term
        })
        self.invoice_id = invoice_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def prepare_invoice_line(self, lines_record, type):
        lines = []
        if type == 'services':
            for data in lines_record:
                lines.append((0, 0, {
                    'product_id': data.product_id.id,
                    'name': data.name,
                    'quantity': data.qty,
                    'product_uom_id': data.uom_id.id,
                    'price_unit': data.price,
                    'tax_ids': [(6, 0, data.tax_ids.ids)] if data.tax_ids else False
                }))
        if type in ['default_product', 'additional_product']:
            for data in lines_record:
                desc = data.name + "\n Service Used :" + data.service_id.name
                lines.append((0, 0, {
                    'product_id': data.product_id.id,
                    'name': desc,
                    'quantity': data.qty,
                    'product_uom_id': data.uom_id.id,
                    'price_unit': data.price,
                    'tax_ids': [(6, 0, data.tax_ids.ids)] if data.tax_ids else False
                }))
        return lines

    # Send Updated Quote Mail
    def action_send_update_quot(self):
        additional_part = self.inspection_required_parts_ids.filtered(
            lambda line: line.is_additional_part and line.additional_part_status == 'pending').mapped('id')
        data = {
            'additional_part_ids': [(6, 0, additional_part)],
            'inspection_id': self.id,
            'quote_state': 'sent',
            'quotation_sent_date_time': fields.Datetime.now(),
        }
        part_id = self.env['additional.part.confirmation'].create(data)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/vehicle-service/job-card/additional-part/' + part_id.access_token
        ctx = {
            'url': url,
            'expiry_date': str(part_id.quote_expire_date.strftime('%Y-%m-%d'))
        }
        template_id = self.env.ref('tk_vehicle_management.customer_inspection_update_quotation_mail_template').sudo()
        self.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(self.id, force_send=True)
        self.action_send_additional_quot_whatsapp_message()
        self.update_quot_mail = False

    # Quotation Resend Mail
    def action_resend_quotation(self):
        self.write({
            'quote_state': 'sent',
            'is_expired': False,
            'quot_reopen_request': 'draft',
            'quotation_sent_date_time': fields.Datetime.now(),
            'part_selected': False,
            'service_selected': False,
        })
        # Services
        self.inspection_required_service_ids.write({'service_selected': False})
        unselected_services = self.env['vehicle.required.services'].sudo().search(
            [('vehicle_health_report_id', '=', self.vehicle_health_report_id.id),
             ('active', '=', False)])
        unselected_services.write({'active': True})
        # Parts
        self.inspection_required_parts_ids.write({'part_selected': False})
        unselected_parts = self.env['vehicle.required.parts'].sudo().search(
            [('vehicle_health_report_id', '=', self.vehicle_health_report_id.id),
             ('active', '=', False)])
        unselected_parts.write({'active': True})
        # Resend Quotation
        mail_template = self.env.ref('tk_vehicle_management.customer_inspection_quotation_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        # Resend Whatsapp Quotation
        self.action_send_quot_whatsapp_message()

    # Quotation Details & Sign
    def _has_to_be_signed(self):
        self.ensure_one()
        return (
                self.quote_state in ['draft', 'sent']
                and not self.is_expired
                and not self.signature
        )

    # Consent Has Signed
    def _consent_has_to_be_signed(self):
        self.ensure_one()
        return (
                self.consent_sent_state in ['draft', 'sent']
                and not self.consent_is_expired
                and not self.customer_signature
        )

    # Consent Resend Mail
    def action_resend_consent(self):
        self.write({
            'consent_sent_state': 'sent',
            'consent_is_expired': False,
            'consent_reopen_request': 'draft',
            'consent_sent_date_time': fields.Datetime.now(),
        })
        wa_template_id = self.get_whatsapp_template(template_id='tk_vehicle_management.wa_consent_template_id')
        if not wa_template_id:
            return
        mobile_no = self.check_whatsapp_phone(self.customer_id)
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)

    # Portal Access For Customer
    def action_customer_grand_portal_access(self):
        inspection_id = self.env['vehicle.inspection'].browse(self._context.get('active_id'))
        portal_wizard = self.env['portal.wizard'].sudo().create(
            {'partner_ids': [(6, 0, [inspection_id.customer_id.id])]})
        return portal_wizard._action_open_modal()

    # Send Quotation Whatsapp Message
    def action_send_quot_whatsapp_message(self):
        wa_template_id = self.get_whatsapp_template(template_id='tk_vehicle_management.wa_quot_template_id')
        if not wa_template_id:
            return
        mobile_no = self.check_whatsapp_phone(self.customer_id)
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)

    def send_whatsapp_qc_checks(self):
        wa_template_id = self.get_whatsapp_template(
            template_id='tk_vehicle_management.wa_qc_check_complete_template_id')
        if not wa_template_id:
            return
        mobile_no = self.check_whatsapp_phone(self.sale_person_id.partner_id)
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)

    # Sent Additional Part Quotation Message
    def action_send_additional_quot_whatsapp_message(self):
        wa_template_id = self.get_whatsapp_template(template_id='tk_vehicle_management.wa_additional_quot_template_id')
        if not wa_template_id:
            return
        mobile_no = self.check_whatsapp_phone(self.customer_id)
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)

    # Send Whatsapp Message
    def check_whatsapp_phone(self, partner_id):
        # Check WhatsApp Phone No
        mobile_no = False
        if partner_id.mobile:
            mobile_no = partner_id.mobile
        elif partner_id.phone:
            mobile_no = partner_id.phone
        return mobile_no

    def get_whatsapp_template(self, template_id):
        # Get Template from Settings
        wa_template_id = False
        config_template_id = self.env['ir.config_parameter'].sudo().get_param(template_id)
        if config_template_id:
            wa_template_id = self.env['whatsapp.template'].sudo().browse(int(config_template_id))
        return wa_template_id

    def _get_html_preview_whatsapp(self, wa_template_id, rec):
        # Prepare Body of whatsapp Message
        """This method is used to get the html preview of the whatsapp message."""
        self.ensure_one()
        # No of Text
        number_of_free_text = len(wa_template_id.variable_ids.filtered(
            lambda line: line.field_type == 'free_text' and line.line_type == 'body'))
        # Header Text
        header_text_1 = False
        if wa_template_id.header_type == 'text':
            header_params = wa_template_id.variable_ids.filtered(lambda line: line.line_type == 'header')
            if wa_template_id.variable_ids and header_params:
                header_param = header_params[0]
                if header_param.field_type == 'free_text' and not header_text_1:
                    header_text_1 = header_param.demo_value
        # Prepare Body
        template_variables_value = wa_template_id.variable_ids._get_variables_value(rec)
        text_vars = wa_template_id.variable_ids.filtered(lambda var: var.field_type == 'free_text')
        for var_index, body_text_var in zip(range(1, number_of_free_text + 1),
                                            text_vars.filtered(lambda var: var.line_type == 'body')):
            free_text_x = self[f'free_text_{var_index}']
            if free_text_x:
                template_variables_value[f'body-{body_text_var.name}'] = free_text_x
        if header_text_1 and text_vars.filtered(lambda var: var.line_type == 'header'):
            template_variables_value['header-{{1}}'] = self.header_text_1
        return wa_template_id._get_formatted_body(variable_values=template_variables_value)

    def action_send_whatsapp_message(self, phone, wa_template_id):
        # Send Whatsapp Message
        body = self._get_html_preview_whatsapp(wa_template_id, self)
        post_values = {'body': body,
                       'message_type': 'whatsapp_message',
                       'partner_ids': [self.env.user.partner_id.id], }
        message = self.env['mail.message'].create(dict(post_values, res_id=self.id, model=wa_template_id.model,
                                                       subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                                                           "mail.mt_note")))
        message = self.env['whatsapp.message'].sudo().create({
            'mobile_number': phone,
            'wa_template_id': wa_template_id.id,
            'wa_account_id': wa_template_id.wa_account_id.id,
            'mail_message_id': message.id,
        })
        message._send(force_send_by_cron=True)

    # Print Gate Pass - Button
    def action_print_gate_pass(self):
        if not self.invoice_id.amount_residual == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Invoice Pending !'),
                    'message': _(
                        'The invoice has not been paid yet. Kindly settle the payment to print the gate pass'),
                    'sticky': False,
                }}
        report_id = self.env.ref('tk_vehicle_management.action_vehicle_service_gate_pass_qweb_report')
        if report_id:
            return report_id.report_action(self)

    # Button : Complete all check point
    def action_check_complete(self):
        self.vehicle_qc_check_ids.filtered(lambda line: not (
                line.required_attention or line.further_attention or line.okay_for_now) and not line.display_type).write(
            {
                'okay_for_now': True
            })

    # Smart Button
    def action_vehicle_health_report(self):
        if not self.vehicle_health_report_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card',
            'res_model': 'vehicle.health.report',
            'res_id': self.vehicle_health_report_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'project.task',
            'domain': [('inspection_id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'kanban,tree,form',
            'target': 'current'
        }

    def action_view_delivery_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'domain': [('job_card_id', '=', self.id), ('picking_type_code', '=', 'outgoing')],
            'context': {'create': False},
            'view_mode': 'tree,kanban,form',
            'target': 'current'
        }

    def action_view_return_delivery_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Return Delivery Orders',
            'res_model': 'stock.picking',
            'domain': [('job_card_id', '=', self.id), ('picking_type_code', '=', 'incoming')],
            'context': {'create': False},
            'view_mode': 'tree,kanban,form',
            'target': 'current'
        }

    def action_view_job_card_invoice(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('job_card_id', '=', self.id)],
            'context': {'default_job_card_id': self.id, 'default_move_type': 'out_invoice'},
            'view_mode': 'tree,kanban,form',
            'target': 'current'
        }
        return action

    def action_view_unselect_services(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Unselected Services',
            'res_model': 'vehicle.required.services',
            'domain': [('vehicle_health_report_id', '=', self.vehicle_health_report_id.id), ('active', '=', False),
                       ('display_type', '=', False), ('service_selected', '=', False)],
            'context': {'create': False},
            'view_mode': 'tree',
            'target': 'current'
        }
        return action

    def action_view_unselect_parts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Unselected Parts',
            'res_model': 'vehicle.required.parts',
            'domain': [('vehicle_health_report_id', '=', self.vehicle_health_report_id.id),
                       ('active', '=', False),
                       ('display_type', '=', False), ('part_selected', '=', False)],
            'context': {'create': False},
            'view_mode': 'tree',
            'target': 'current'
        }

    # Scheduler
    @api.model
    def expire_vehicle_quotation(self):
        today_date = fields.Date.today()
        job_card_obj = self.env['vehicle.inspection'].sudo()
        # Job Card Quotation
        quotation_rec = job_card_obj.search([('status', '=', 'quotation'), ('quote_state', '=', 'sent')])
        for data in quotation_rec:
            if today_date > data.quote_expire_date:
                data.is_expired = True
                data.quote_state = 'expire'
        # Additional Part Quotation Expire
        additional_part_quotation = job_card_obj.search([('status', '=', 'in_repair')])
        for rec in additional_part_quotation:
            for data in rec.additional_parts_quot_ids:
                if today_date > data.quote_expire_date and data.quote_state == 'sent':
                    data.is_expired = True
                    data.quote_state = 'expire'

    @api.model
    def expire_vehicle_consent(self):
        today_date = fields.Date.today()
        job_card_obj = self.env['vehicle.inspection'].sudo()
        # Job Card Consent
        consent_rec = job_card_obj.search([('status', '=', 'concern'), ('consent_sent_state', '=', 'sent')])
        for data in consent_rec:
            if today_date > data.consent_expire_date:
                data.consent_is_expired = True
                data.consent_sent_state = 'expire'

    # Portal Url
    def get_portal_url(self, type):
        url = '/my/vehicle/' + type + '/form/' + self.access_token
        return url


# Inspection CheckList
class InspectionCheckList(models.Model):
    _name = 'inspection.checklist'
    _description = 'Inspection CheckList'

    sequence = fields.Integer()
    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char(string="Description", translate=True)
    display_type = fields.Selection(selection=[('line_section', "Section"), ('line_note', "Note")], default=False)
    is_check = fields.Boolean(string="Check")
    inspection_id = fields.Many2one('vehicle.inspection')


# Inner Body Images
class InspectionInnerImages(models.Model):
    _name = 'inspection.inner.images'
    _description = "Vehicle Job Card Inner Images"

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    inspection_id = fields.Many2one('vehicle.inspection')


# Outer Body Images
class InspectionOuterImages(models.Model):
    _name = 'inspection.outer.images'
    _description = "Job Card Outer Images"

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    inspection_id = fields.Many2one('vehicle.inspection')


# Other Images
class InspectionOtherImages(models.Model):
    _name = 'inspection.other.images'
    _description = "Vehicle Job Card Other Images"

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    inspection_id = fields.Many2one('vehicle.inspection')


# Inspection Qc Check
class InspectionQcCheck(models.Model):
    _name = 'inspection.qc.check'
    _description = 'Inspection Quality Check'
    _rec_name = 'task_id'

    inspection_id = fields.Many2one('vehicle.inspection')
    datetime = fields.Datetime(string="Datetime", default=fields.Datetime.now())
    task_id = fields.Many2one('project.task', string="Task")
    is_passes = fields.Boolean(string="Is Passed")
    is_reject = fields.Boolean(string="Is Reject")

    def action_status_approve(self):
        self.task_id.task_state = 'complete'
        body_inspection = Markup(
            'Task : <strong>' + str(self.task_id.name) + '</strong><br/>Status : <strong>Approve (Qc Check)</strong>')
        body = Markup('<strong>Qc Check Passed</strong>')
        self.inspection_id.message_post(body=body_inspection, message_type="notification",
                                        partner_ids=[self.env.user.partner_id.id])
        self.task_id.message_post(body=body, message_type="notification", partner_ids=[self.env.user.partner_id.id])
        self.is_passes = True


class InspectionConcern(models.Model):
    _name = 'inspection.concern'
    _description = "Inspection Concern"

    inspection_id = fields.Many2one('vehicle.inspection', string="Vehicle Job Card")
    concern_type_id = fields.Many2one('concern.type', string="Concern", )
    name = fields.Text(string="Description")
    display_type = fields.Selection(selection=[('line_section', "Section"),
                                               ('line_note', "Note")], default=False)
    sequence = fields.Integer()


# Additional Part Confirmation
class AdditionalPartConfirmation(models.Model):
    _name = 'additional.part.confirmation'
    _description = "Additional Part Confirmation"

    inspection_id = fields.Many2one('vehicle.inspection', string="Vehicle Job Card")
    additional_part_ids = fields.Many2many('vehicle.required.parts', string="Additional Required Parts")
    access_token = fields.Char(string="Access Token")
    quote_state = fields.Selection([('draft', "Draft"),
                                    ('sent', "Sent"),
                                    ('signed', "Signed & Accepted"),
                                    ('reject', "Rejected"),
                                    ('expire', 'Expired'),
                                    ('cancel', "Cancelled")], string="Status", default='draft')
    is_expired = fields.Boolean(string="Is Quotation Expired")
    quotation_sent_date_time = fields.Datetime(string="Sent Date Time")
    quote_accept_date_time = fields.Datetime(string="Accepted Date Time")
    quote_expire_date = fields.Date(string="Expire Date", compute="compute_quot_expire_date")
    signature = fields.Image(string="Signature")
    quote_reject_reason = fields.Text(string="Quotation Reject Reason")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    total_amount = fields.Monetary(string="Total Amount", compute="compute_total_amount")
    # Quote Url
    quote_url = fields.Char(string="Quotation URL", compute="compute_quotation_url")

    # ConfirmSelection
    confirm_selection = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['access_token'] = str(uuid.uuid4())
        res = super(AdditionalPartConfirmation, self).create(vals_list)
        return res

    # Quotation Expire Date
    @api.depends('quotation_sent_date_time')
    def compute_quot_expire_date(self):
        for rec in self:
            date = False
            expire_config_days = self.env['ir.config_parameter'].sudo().get_param(
                'tk_vehicle_management.quot_expire_days')
            expire_days = int(expire_config_days) if expire_config_days else 7
            if rec.quotation_sent_date_time:
                date = rec.quotation_sent_date_time + relativedelta(days=expire_days)
            rec.quote_expire_date = date

    def _has_to_be_signed(self):
        self.ensure_one()
        return (
                self.quote_state in ['draft', 'sent']
                and not self.is_expired
                and not self.signature
        )

    # Quotation URL
    @api.depends('access_token', 'inspection_id')
    def compute_quotation_url(self):
        for rec in self:
            url = ""
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if rec.access_token and base_url:
                url = base_url + '/vehicle-service/job-card/additional-part/' + rec.access_token
            rec.quote_url = url

    @api.depends('additional_part_ids')
    def compute_total_amount(self):
        for rec in self:
            total = 0.0
            for data in rec.additional_part_ids:
                if data.additional_part_selected:
                    total = total + data.total_amount
            rec.total_amount = total

    def action_reopen_additional_quotation(self):
        self.write({
            'quotation_sent_date_time': fields.Datetime.now(),
            'is_expired': False,
            'signature': False,
            'quote_state': 'sent',
            'confirm_selection': False
        })
        for data in self.additional_part_ids:
            data.additional_part_status = 'pending'
            data.additional_part_rejected = False
            data.additional_part_selected = False
        ctx = {
            'url': self.quote_url,
            'expiry_date': str(self.quote_expire_date.strftime('%Y-%m-%d'))
        }
        template_id = self.env.ref('tk_vehicle_management.customer_inspection_update_quotation_mail_template').sudo()
        self.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(self.inspection_id.id,
                                                                                            force_send=True)
        self.inspection_id.action_send_additional_quot_whatsapp_message()

    def get_portal_url(self):
        url = '/my/vehicle/jc-updated-quot/form/' + self.access_token
        return url


# 3C - Concern
class JobCardConcern(models.Model):
    _name = 'job.card.concern'
    _description = "Job Card Concern"

    sequence = fields.Integer()
    concern = fields.Char()
    cause = fields.Char()
    correction = fields.Char()
    inspection_id = fields.Many2one(comodel_name='vehicle.inspection')


# Quality Checks
class VehicleQualityChecks(models.Model):
    _name = 'vehicle.quality.checks'
    _description = 'Vehicle Quality Checks'

    name = fields.Char(string="Checkpoint")
    inspection_id = fields.Many2one(comodel_name='vehicle.inspection', string="Vehicle Job Card")
    sequence = fields.Integer()
    remark = fields.Char()
    display_type = fields.Selection(selection=[('line_section', "Section"),
                                               ('line_note', "Note")], default=False)
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()

    def action_required_attention_accept(self):
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False

    def action_required_attention_reject(self):
        self.required_attention = False

    def action_further_attention_accept(self):
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False

    def action_further_attention_reject(self):
        self.further_attention = False

    def action_okay_for_now_accept(self):
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False

    def action_okay_for_now_reject(self):
        self.okay_for_now = False
