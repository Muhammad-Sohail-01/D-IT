import secrets
from odoo import api, fields, models, _
from markupsafe import Markup
from odoo.exceptions import ValidationError


def combine_dicts_by_key(data_dict):
    def combine_dicts(lst):
        combined_dict = {}
        for d in lst:
            for key, value in d.items():
                if key in combined_dict:
                    combined_dict[key] += value
                else:
                    combined_dict[key] = value
        return combined_dict

    processed_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, list):
            processed_dict[key] = [combine_dicts(value)]
        else:
            processed_dict[key] = value
    return processed_dict


def get_requirement_status(must_required, okay_for_now, further_inspection):
    if must_required:
        return 'must_required'
    elif okay_for_now:
        return 'okay'
    elif further_inspection:
        return 'essential'
    else:
        return False


class VehicleHealthReport(models.Model):
    _name = 'vehicle.health.report'
    _description = "Vehicle Health Report"
    _rec_name = 'inspection_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Inspection
    inspection_id = fields.Many2one('vehicle.inspection', string="Job Card", ondelete='cascade')
    status = fields.Selection([('draft', 'Draft'),
                               ('in_progress', 'In Progress'),
                               ('complete', 'Complete')],
                              default='draft')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')

    # Responsible
    sale_person_id = fields.Many2one(related="inspection_id.sale_person_id", string="Receptionist",
                                     store=True)
    service_adviser_id = fields.Many2one(related="inspection_id.service_adviser_id",
                                         string="Service Advisor",
                                         store=True)
    # Task Details
    task_id = fields.Many2one('project.task', string="Task")
    inspection_type_id = fields.Many2one('inspection.type', string="Inspection Type ")
    allocated_hours = fields.Float(related="task_id.allocated_hours", string="Allotted Hours")

    # Vehicle Details
    brand_id = fields.Many2one(related="inspection_id.brand_id", string="Vehicle Brand")
    vehicle_model_id = fields.Many2one(related="inspection_id.vehicle_model_id", string="Model", )
    fuel_type = fields.Selection(related="inspection_id.fuel_type", string='Fuel Type')
    transmission = fields.Selection(related="inspection_id.transmission")
    vin_no = fields.Char(related="inspection_id.vin_no", string="VIN No.")
    registration_no = fields.Char(related="inspection_id.registration_no", string="Registration No")
    miles = fields.Integer(related="inspection_id.miles", string="Kilometers")
    year = fields.Char(related="inspection_id.year", string="Year")
    color = fields.Selection(related="inspection_id.color", string="Color")
    is_warranty = fields.Boolean(related="inspection_id.is_warranty", string="Warranty")
    warranty_type = fields.Selection(related="inspection_id.warranty_type",
                                     string="Type of Warranty")
    insurance_provider = fields.Char(related="inspection_id.insurance_provider",
                                     string="Insurance Provider")

    # Inspection Details
    inspect_type = fields.Selection(related="inspection_id.inspect_type", string="Inspection Type")
    inspection_type = fields.Selection(related="inspection_id.inspection_type",
                                       string="Type of Inspection")

    # Specific Inspection
    part_assessment = fields.Boolean(string="Part Assessment")
    inner_body_inspection = fields.Boolean(string="Interior")
    outer_body_inspection = fields.Boolean(string="Exterior")
    mechanical_condition = fields.Boolean(string="Under Hood / Mechanical Inspection")
    vehicle_fluid = fields.Boolean(string="Fluids")
    tyre_inspection = fields.Boolean(string="Tyre")
    under_vehicle = fields.Boolean(string="Under Vehicle")
    brake_condition = fields.Boolean(string="Brake Conditions")
    vehicle_component = fields.Boolean(string="Multi Point")

    # Customer Observation
    customer_observation = fields.Text(related="inspection_id.customer_observation")

    # Team Details
    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids", string="Team Leaders ")
    team_technician_ids = fields.Many2many(related="team_id.technician_ids",
                                           string="Team Technicians")
    # leaders_ids = fields.Many2many('res.users', string="Team Leaders",
    #                                domain="[('id','in',team_leaders_ids)]")
    # technician_ids = fields.Many2many('res.users', 'vhr_technician_rel', 'vhr_technician_id',
    #                                   'vhr_user_technician_id', string="Technicians",
    #                                  domain="[('id','in',team_technician_ids)]")

    leaders_ids = fields.Many2many('hr.employee', string="Team Leaders")

    technician_ids = fields.Many2many('hr.employee', 'vhr_technician_rel', 'vhr_technician_id',
                                      'vhr_user_technician_id', string="Technicians",
                                      domain=[('technician', '=', True)])

    # Part Assessment
    wd = fields.Boolean(string="4WD")
    abs = fields.Boolean(string="ABS")
    awd = fields.Boolean(string="AWD")
    gps = fields.Boolean(string="GPS")
    stereo = fields.Boolean(string="Stereo")
    bed_liner = fields.Boolean(string="Bedliner")
    wide_tires = fields.Boolean(string="Wide Tires")
    power_locks = fields.Boolean(string="Power Locks")
    power_seats = fields.Boolean(string="Power Seats")
    power_windows = fields.Boolean(string="Power Windows")
    running_boards = fields.Boolean(string="Running Boards")
    roof_rack = fields.Boolean(string="Roof Rack")
    camper_shell = fields.Boolean(string="Camper Shell")
    sport_wheels = fields.Boolean(string="Sport Wheels")
    tilt_wheel = fields.Boolean(string="Tilt Wheel")
    cruise_control = fields.Boolean(string="Cruise Control")
    cvt_transmission = fields.Boolean(string="CVT Transmission")
    infotainment_system = fields.Boolean(string="Infotainment System")
    moon_sun_roof = fields.Boolean(string="Moon or Sun Roof")
    rear_sliding_window = fields.Boolean(string="Rear Sliding Window")
    rear_window_wiper = fields.Boolean(string="Rear Window Wiper")
    rear_lift_gate = fields.Boolean(string="Rear Liftgate")
    air_conditioning = fields.Boolean(string="Air Conditioning")
    leather_interior = fields.Boolean(string="Leather Interior")
    towing_package = fields.Boolean(string="Towing Package")
    auto_transmission = fields.Boolean(string="Automatic Transmission")
    am_fm_radio = fields.Boolean(string="AM / FM / Sirius Radio")
    cd_usb_bluetooth = fields.Boolean(string="CD / USB / Bluetooth")
    luxury_sport_pkg = fields.Boolean(string="Luxury / Sport pkg.")
    other = fields.Boolean(string="Other")

    # Vehicle Body Inner Conditions
    vehicle_inner_inspection_ids = fields.One2many(comodel_name='vehicle.interior.condition',
                                                   inverse_name='inspection_id')

    # Vehicle Body Outer Conditions
    vehicle_outer_inspection_ids = fields.One2many(comodel_name='vehicle.outer.condition',
                                                   inverse_name='inspection_id')

    # Mechanical Conditions
    vehicle_mechanical_inspection_ids = fields.One2many(comodel_name='mechanical.condition.line',
                                                        inverse_name='inspection_id')

    # Vehicle Components
    vehicle_components_inspection_ids = fields.One2many(comodel_name='vehicle.components.line',
                                                        inverse_name='inspection_id', )

    # Vehicle Fluids
    vehicle_fluid_inspection_ids = fields.One2many(comodel_name='vehicle.fluids.line',
                                                   inverse_name='inspection_id')

    # Tyres Inspections
    vehicle_tyre_inspection_ids = fields.One2many(comodel_name='tyre.inspection.line',
                                                  inverse_name='inspection_id')

    # Under Vehicle
    under_vehicle_inspection_ids = fields.One2many(comodel_name='under.vehicle.inspection.line',
                                                   inverse_name='inspection_id')

    # Brakes Conditions
    brake_condition_ids = fields.One2many(comodel_name='brake.condition.line',
                                          inverse_name='inspection_id')

    # Inspection Image
    inspection_image_ids = fields.One2many(comodel_name='inspection.images',
                                           inverse_name='inspection_id')

    # Required Services
    inspection_required_service_ids = fields.One2many(comodel_name='vehicle.required.services',
                                                      inverse_name='vehicle_health_report_id',
                                                      string="Inspection Required Services")

    # Required Parts
    inspection_required_parts_ids = fields.One2many(comodel_name='vehicle.required.parts',
                                                    inverse_name='vehicle_health_report_id',
                                                    string="Inspection Required Parts")

    # Total Amount
    service_total = fields.Monetary(string="Service Total", compute="_compute_total")
    parts_total = fields.Monetary(string="Parts Total", compute="_compute_total")
    service_tax_amount = fields.Monetary(string="Service Tax", compute="_compute_total")
    part_tax_amount = fields.Monetary(string="Part Tax", compute="_compute_total")
    untaxed_service_amount = fields.Monetary(string="Untaxed Service Amount",
                                             compute="_compute_total")
    untaxed_part_amount = fields.Monetary(string="Untaxed Part Amount", compute="_compute_total")

    # Template
    template_id = fields.Many2one(comodel_name='health.report.template', string="Template")

    # Taxes
    tax_ids = fields.Many2many('account.tax', string="Taxes")

    # Technician User
    is_technician_user = fields.Boolean(compute="_compute_is_technician_user")

    # DEPRECATED
    milage = fields.Char(related="inspection_id.milage", string="Milage")

    # Unlink
    def unlink(self):
        for rec in self:
            if rec.task_id:
                rec.task_id.unlink()
            return super(VehicleHealthReport, self).unlink()

    # Smart Button
    def action_view_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'project.task',
            'res_id': self.task_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    # Total Service and Parts
    @api.depends('inspection_required_service_ids', 'inspection_required_parts_ids', 'tax_ids')
    def _compute_total(self):
        for rec in self:
            service_rec = rec.mapped('inspection_required_service_ids')
            part_rec = rec.mapped('inspection_required_parts_ids')
            service_total = sum(service_rec.mapped('total_amount'))
            parts_total = sum(part_rec.mapped('total_amount'))
            service_tax = sum(service_rec.mapped('tax_amount'))
            part_tax = sum(part_rec.mapped('tax_amount'))
            rec.service_total = service_total
            rec.parts_total = parts_total
            rec.service_tax_amount = service_tax
            rec.part_tax_amount = part_tax
            rec.untaxed_service_amount = service_total - service_tax
            rec.untaxed_part_amount = parts_total - part_tax

    # Button Method
    def action_in_progress_inspection(self):
        """In progress inspection"""
        self.status = 'in_progress'

    def action_add_service_parts(self):  # Add Parts and Services from inspection tabs
        # self.inspection_required_service_ids = [(5, 0, 0)]
        # self.inspection_required_parts_ids = [(5, 0, 0)]
        inspections = [
            (self.outer_body_inspection, self.vehicle_outer_inspection_ids, 'Exterior Services',
             'Exterior Service Parts'),
            (self.inner_body_inspection, self.vehicle_inner_inspection_ids, 'Interior Services',
             'Interior Service Parts'),
            (self.mechanical_condition, self.vehicle_mechanical_inspection_ids,
             'Under Hood Services',
             'Under Hood Service Parts'),
            (self.vehicle_fluid, self.vehicle_fluid_inspection_ids, 'Fluid Services',
             'Fluid Service Parts'),
            (self.tyre_inspection, self.vehicle_tyre_inspection_ids, 'Tyre Services',
             'Tyre Service Parts'),
            (self.under_vehicle, self.under_vehicle_inspection_ids, 'Under Vehicle Services',
             'Under Vehicle Service Parts'),
            (self.brake_condition, self.brake_condition_ids, 'Brake Services',
             'Brake Service Parts'),
            (self.vehicle_component, self.vehicle_components_inspection_ids, 'Multi-Point Services',
             'Multi-Point Service Parts'),
        ]
        for inspection_flag, inspection_ids, service_name, part_name in inspections:
            if inspection_flag and inspection_ids:
                self.get_services_from_inspection(inspection_ids, service_name)
                self.get_parts_from_inspection(inspection_ids, part_name)
        self.status = 'complete'

    def get_services_from_inspection(self, inspections, section):
        # If Not Service Than Return
        is_any_services = inspections.mapped('service_ids')
        if not is_any_services:
            return
        self.env['vehicle.required.services'].create({
            'display_type': 'line_section',
            'name': section,
            'inspection_id': self.inspection_id.id,
            'vehicle_health_report_id': self.id
        })
        for rec in inspections:
            required_status = get_requirement_status(must_required=rec.required_attention,
                                                     okay_for_now=rec.okay_for_now,
                                                     further_inspection=rec.further_attention)
            for data in rec.service_ids:
                service_id = self.env['vehicle.required.services'].create({
                    'display_type': False,
                    'vehicle_health_report_id': self.id,
                    'inspection_id': self.inspection_id.id,
                    'product_id': data.id,
                    'price': data.lst_price,
                    'required_status': required_status,
                    'name': data.name + "(" + str(rec.part_id.name) + ")",
                    'estimate_time': data.estimate_time,
                    'tax_ids': [(6, 0, self.tax_ids.ids)]
                })
                # Assign Service Line to Parts
                for part in rec.part_ids.filtered(lambda line: line.service_id.id == data.id):
                    part.service_line_id = service_id.id

    def get_parts_from_inspection(self, parts, section):
        # Required Parts Section
        is_any_part = parts.mapped('part_ids')
        if not is_any_part:
            return
        self.env['vehicle.required.parts'].create({
            'display_type': 'line_section',
            'vehicle_health_report_id': self.id,
            'inspection_id': self.inspection_id.id,
            'name': section,
        })
        for rec in parts:
            required_status = get_requirement_status(must_required=rec.required_attention,
                                                     okay_for_now=rec.okay_for_now,
                                                     further_inspection=rec.further_attention)
            for data in rec.part_ids:
                self.env['vehicle.required.parts'].create({
                    'display_type': False,
                    'vehicle_health_report_id': self.id,
                    'inspection_id': self.inspection_id.id,
                    'product_id': data.product_id.id,
                    'name': data.product_id.name,
                    'service_id': data.service_line_id.id,
                    'price': data.product_id.lst_price,
                    'required_status': required_status,
                    'qty': data.qty,
                    'tax_ids': [(6, 0, self.tax_ids.ids)]
                })

    # Template
    @api.onchange('template_id')
    def onchange_health_report_template(self):  # Get Template Inspection Data
        for rec in self:
            template = rec.template_id

            # Clear existing inspections
            rec.vehicle_inner_inspection_ids = [(5, 0, 0)]
            rec.vehicle_outer_inspection_ids = [(5, 0, 0)]
            rec.vehicle_mechanical_inspection_ids = [(5, 0, 0)]
            rec.vehicle_components_inspection_ids = [(5, 0, 0)]
            rec.vehicle_fluid_inspection_ids = [(5, 0, 0)]
            rec.vehicle_tyre_inspection_ids = [(5, 0, 0)]
            rec.brake_condition_ids = [(5, 0, 0)]
            rec.under_vehicle_inspection_ids = [(5, 0, 0)]

            # Assign template boolean values
            rec.inner_body_inspection = template.inner_body_inspection
            rec.outer_body_inspection = template.outer_body_inspection
            rec.mechanical_condition = template.mechanical_condition
            rec.vehicle_component = template.vehicle_component
            rec.vehicle_fluid = template.vehicle_fluid
            rec.tyre_inspection = template.tyre_inspection
            rec.brake_condition = template.brake_condition
            rec.under_vehicle = template.under_vehicle

            # Populate inspection lines if the corresponding inspection is enabled in the template
            if template.inner_body_inspection:
                inner_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_inner_body_parts_ids
                ]
                rec.vehicle_inner_inspection_ids = inner_lines

            if template.outer_body_inspection:
                outer_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_outer_body_parts_ids
                ]
                rec.vehicle_outer_inspection_ids = outer_lines

            if template.mechanical_condition:
                mechanical_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_mechanical_parts_ids
                ]
                rec.vehicle_mechanical_inspection_ids = mechanical_lines

            if template.vehicle_component:
                component_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_component_parts_ids
                ]
                rec.vehicle_components_inspection_ids = component_lines

            if template.vehicle_fluid:
                fluid_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_fluid_parts_ids
                ]
                rec.vehicle_fluid_inspection_ids = fluid_lines

            if template.tyre_inspection:
                tyre_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_tyre_parts_ids
                ]
                rec.vehicle_tyre_inspection_ids = tyre_lines

            if template.brake_condition:
                brake_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_brake_parts_ids
                ]
                rec.brake_condition_ids = brake_lines

            if template.under_vehicle:
                under_vehicle_lines = [
                    (0, 0, {'part_id': data.id})
                    for data in template.vehicle_under_vehicle_parts_ids
                ]
                rec.under_vehicle_inspection_ids = under_vehicle_lines

    # Check All Button
    def action_check_okay_inspections(self):
        check_all = self._context.get('check_all')
        part_data = False
        if check_all == 'interior':
            part_data = self.vehicle_inner_inspection_ids
        elif check_all == 'exterior':
            part_data = self.vehicle_outer_inspection_ids
        elif check_all == 'under_hood':
            part_data = self.vehicle_mechanical_inspection_ids
        elif check_all == 'fluid':
            part_data = self.vehicle_fluid_inspection_ids
        elif check_all == 'tyre':
            part_data = self.vehicle_tyre_inspection_ids
        elif check_all == 'under_vehicle':
            part_data = self.under_vehicle_inspection_ids
        elif check_all == 'brake':
            part_data = self.brake_condition_ids
        elif check_all == 'multi_point':
            part_data = self.vehicle_components_inspection_ids
        if part_data:
            part_data.filtered(lambda
                                   line: not line.required_attention and not line.further_attention and not line.okay_for_now).write(
                {
                    'okay_for_now': True
                })

    # Check ifn user is technician
    @api.depends('status')
    def _compute_is_technician_user(self):
        for rec in self:
            is_technician_user = False
            if self.env.user.has_group('tk_vehicle_management.vehicle_technician'):
                is_technician_user = True
            rec.is_technician_user = is_technician_user


# -------------------------Health Report Images------------------------------
class InspectionImages(models.Model):
    _name = 'inspection.images'
    _description = "Inspection Images"

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    inspection_id = fields.Many2one('vehicle.health.report')


# --------------------------Required Services-------------------------------
class VehicleRequiredServices(models.Model):
    _name = 'vehicle.required.services'
    _description = 'Vehicle Required Services'

    product_id = fields.Many2one('product.product', string="Service",
                                 domain="[('detailed_type','=','service')]")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", related="estimate_time", store=True)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    price = fields.Monetary(string="Unit Price")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Monetary(string="Tax Amount", compute="_compute_total_amount")
    untaxed_amount = fields.Monetary(string="Untaxed Amount", compute="_compute_total_amount")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount")
    vehicle_health_report_id = fields.Many2one('vehicle.health.report',
                                               string="Vehicle Health Report")
    inspection_id = fields.Many2one(comodel_name='vehicle.inspection')
    estimate_time = fields.Float(string="Estimate Time")
    task_id = fields.Many2one('project.task', string="Task")
    task_state = fields.Selection(related='task_id.task_state', store=True)
    sequence = fields.Integer()
    display_type = fields.Selection(selection=[('line_section', "Section"), ('line_note', "Note")],
                                    default=False)
    active = fields.Boolean(string="Active", default=True)

    # Part Selection
    required_status = fields.Selection([('must_required', 'Requires immediate attention'),
                                        ('essential', 'Requires future attention'),
                                        ('okay', 'Checked and OK at this time')],
                                       default='must_required')
    service_selected = fields.Boolean(string="Service Selected")

    required_attention = fields.Boolean(compute="compute_required_status")
    further_attention = fields.Boolean(compute="compute_required_status")
    okay_for_now = fields.Boolean(compute="compute_required_status")

    # Additional Service Selection
    is_additional_service = fields.Boolean()
    service_rejected = fields.Boolean()
    additional_service_selected = fields.Boolean()
    additional_service_status = fields.Selection([('pending', 'Pending'),
                                                  ('approve', 'Approved'),
                                                  ('reject', 'Rejected')], default='pending')

    # Part Json
    part_json = fields.Json()

    # Boolean to check that line is included in sale order or not
    is_so_created = fields.Boolean()

    # Concern
    concern = fields.Text(string='Concern')
    cause = fields.Text(string='Cause')
    correction = fields.Text(string='Correction')

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.price = rec.product_id.lst_price
            rec.estimate_time = rec.product_id.estimate_time

    @api.depends('qty', 'product_id', 'price', 'tax_ids', 'tax_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0
            tax_amount = 0.0
            if rec.product_id:
                total_tax_percentage = sum(
                    data.amount if data.amount_type != 'group' else sum(
                        data.children_tax_ids.mapped('amount'))
                    for data in rec.tax_ids
                )
                total = rec.qty * rec.price
                tax_amount = total_tax_percentage * total / 100
            rec.total_amount = total + tax_amount
            rec.tax_amount = tax_amount
            rec.untaxed_amount = total

    @api.depends('required_status')
    def compute_required_status(self):
        for rec in self:
            required_attention = False
            further_attention = False
            okay_for_now = False
            if rec.required_status == 'must_required':
                required_attention = True
            elif rec.required_status == 'essential':
                further_attention = True
            elif rec.required_status == 'okay':
                okay_for_now = True
            rec.required_attention = required_attention
            rec.further_attention = further_attention
            rec.okay_for_now = okay_for_now

    def action_view_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'project.task',
            'res_id': self.task_id.id,
            'context': {'create': False},
            'view_mode': 'form',
            'target': 'current'
        }

    def action_require_status(self):
        return

    def action_approve_additional_service(self):
        """Approve Additional Services"""
        self.service_selected = True
        self.additional_service_status = 'approve'

    def action_reject_additional_service(self):
        """Reject Additional Services"""
        self.service_rejected = True
        self.additional_service_status = 'reject'
        related_parts = self.inspection_id.inspection_required_parts_ids.filtered(
            lambda line: line.service_id.id == self.id)
        if related_parts:
            related_parts.action_reject_part()


# --------------------------Required Parts----------------------------------
class VehicleRequiredParts(models.Model):
    _name = 'vehicle.required.parts'
    _description = 'Vehicle Required Parts'

    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    price = fields.Monetary(string="Unit Price")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Monetary(string="Tax Amount", compute="_compute_total_amount")
    untaxed_amount = fields.Monetary(string="Untaxed Amount", compute="_compute_total_amount")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount")
    vehicle_health_report_id = fields.Many2one('vehicle.health.report',
                                               string="Vehicle Health Report")
    inspection_id = fields.Many2one(comodel_name='vehicle.inspection')
    service_ids = fields.Many2many('vehicle.required.services', compute="compute_services")
    service_id = fields.Many2one('vehicle.required.services', string="Vehicle Service")
    forecast_qty = fields.Float(string="Forecast Qty.", compute="compute_forecast_qty")
    is_additional_part = fields.Boolean()
    additional_part_selected = fields.Boolean()
    additional_part_rejected = fields.Boolean()
    additional_part_id = fields.Many2one('task.additional.parts', string="Additional Part Line")
    additional_part_status = fields.Selection([('pending', 'Pending'),
                                               ('approve', 'Approved'),
                                               ('part_request', 'Part Requested'),
                                               ('part_received', 'Part Received'),
                                               ('reject', 'Reject')],
                                              default='pending')
    sequence = fields.Integer()
    display_type = fields.Selection(selection=[('line_section', "Section"), ('line_note', "Note")],
                                    default=False)
    active = fields.Boolean(string="Active", default=True)

    # Part Selection
    required_status = fields.Selection([('must_required', 'Requires immediate attention'),
                                        ('essential', 'Requires future attention'),
                                        ('okay', 'Checked and OK at this time')],
                                       default='must_required')
    part_selected = fields.Boolean(string="Part Selected")

    required_attention = fields.Boolean(compute="compute_required_status")
    further_attention = fields.Boolean(compute="compute_required_status")
    okay_for_now = fields.Boolean(compute="compute_required_status")

    # Additional Part Required Time
    required_time = fields.Float(string="Additional Required Time")

    # Boolean to check that line is included in sale order or not
    is_so_created = fields.Boolean()

    def unlink(self):
        for rec in self:
            if rec.service_id.required_status == 'must_required' and self.required_status == 'must_required':
                msg = "This part is a required component for must required service '" + str(
                    rec.service_id.name) + "'. you can not delete it."
                raise ValidationError(_(msg))
            return super(VehicleRequiredParts, self).unlink()

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.price = rec.product_id.lst_price

    @api.depends('qty', 'product_id', 'price', 'tax_ids', 'tax_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0
            tax_amount = 0.0
            if rec.product_id:
                total_tax_percentage = sum(
                    data.amount if data.amount_type != 'group' else sum(
                        data.children_tax_ids.mapped('amount'))
                    for data in rec.tax_ids
                )
                total = rec.qty * rec.price
                tax_amount = total_tax_percentage * total / 100
            rec.total_amount = total + tax_amount
            rec.tax_amount = tax_amount
            rec.untaxed_amount = total

    @api.depends('vehicle_health_report_id', 'service_id', 'inspection_id',
                 'vehicle_health_report_id.inspection_required_service_ids')
    def compute_services(self):
        for rec in self:
            vehicle_health_report_id = rec.vehicle_health_report_id
            if self._context.get('from_inspection'):
                vehicle_health_report_id = rec.inspection_id
            rec.service_ids = vehicle_health_report_id.inspection_required_service_ids.filtered(
                lambda line: not line.display_type).mapped(
                'id')

    @api.depends('product_id')
    def compute_forecast_qty(self):
        for rec in self:
            qty = 0.0
            if rec.product_id:
                warehouse_id = rec.product_id.property_stock_inventory.warehouse_id
                qty = rec.product_id.with_context(warehouse=warehouse_id.id).virtual_available
            rec.forecast_qty = qty

    @api.depends('required_status')
    def compute_required_status(self):
        for rec in self:
            required_attention = False
            further_attention = False
            okay_for_now = False
            if rec.required_status == 'must_required':
                required_attention = True
            elif rec.required_status == 'essential':
                further_attention = True
            elif rec.required_status == 'okay':
                okay_for_now = True
            rec.required_attention = required_attention
            rec.further_attention = further_attention
            rec.okay_for_now = okay_for_now

    def action_view_forecast_report(self):
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'target': 'current',
        }
        if self.product_id:
            action['context'][
                'warehouse'] = self.product_id.property_stock_inventory.warehouse_id.id
        return action

    def action_approve_part(self):
        if not self.service_id.service_selected:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Service Selection Pending !'),
                    'message': _('The related service for this part has not been selected yet.'),
                    'sticky': False,
                }}
        self.additional_part_status = 'approve'
        body = Markup('Additional Part Confirmation : <br/>Part Name : <strong>' + str(
            self.product_id.name) + '</strong><br/>Status : <strong>Approved</strong>')
        self.vehicle_health_report_id.inspection_id.message_post(body=body,
                                                                 message_type="notification",
                                                                 partner_ids=[
                                                                     self.env.user.partner_id.id])
        if self.additional_part_id:
            self.additional_part_id.task_id.message_post(body=body,
                                                         message_type="notification",
                                                         partner_ids=[self.env.user.partner_id.id])
            self.additional_part_id.task_id.allocated_hours = self.additional_part_id.task_id.allocated_hours + self.required_time
        self.service_id.estimate_time = self.service_id.estimate_time + self.required_time

    def action_material_arrived(self):
        self.additional_part_status = 'part_received'
        body = Markup('Additional Part Arrived : <br/>Part Name : <strong>' + str(
            self.product_id.name) + '</strong><br/>Status : <strong>Arrived</strong>')
        self.vehicle_health_report_id.inspection_id.message_post(body=body,
                                                                 message_type="notification",
                                                                 partner_ids=[
                                                                     self.env.user.partner_id.id])
        if self.additional_part_id:
            self.additional_part_id.task_id.message_post(body=body,
                                                         message_type="notification",
                                                         partner_ids=[self.env.user.partner_id.id])
            self.additional_part_id.status = 'arrived'

    def action_reject_part(self):
        self.additional_part_status = 'reject'
        if self.additional_part_id:
            self.additional_part_id.status = 'reject'

    def action_reject_part_user(self):
        body = Markup('Additional Part Confirmation : <br/>Part Name : <strong>' + str(
            self.name) + '<br/></strong>Status</strong>:  Reject ')
        self.vehicle_health_report_id.inspection_id.message_post(body=body,
                                                                 message_type="notification",
                                                                 partner_ids=[
                                                                     self.env.user.partner_id.id])
        self.additional_part_status = 'reject'
        if self.additional_part_id:
            self.additional_part_id.task_id.message_post(body=body,
                                                         message_type="notification",
                                                         partner_ids=[self.env.user.partner_id.id])
            self.additional_part_id.status = 'reject'

    def action_require_status(self):
        return


# --------------------------Inspection Conditions-------------------------------
# Vehicle Body Inner Conditions
class VehicleInteriorCondition(models.Model):
    """Vehicle Body Inner Condition"""
    _name = "vehicle.interior.condition"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','interior')]")
    service_ids = fields.Many2many(comodel_name='product.product', relation='in_product_rel',
                                   column1='in_part_id', column2='in_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Inner Conditions Service")
    part_ids = fields.One2many(comodel_name='inner.condition.parts',
                               inverse_name='condition_id',
                               string="Inner Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='interior.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name",
                                      domain="[('item_category', '=', 'interior')]")
    interior_condition = fields.Selection([('worn', "Worn"),
                                           ('burnt', "Burnt"),
                                           ('ripped', "Ripped"),
                                           ('good', "Good"),
                                           ('other', "Other")],
                                          string="Condition")
    interior_condition_notes = fields.Char(string="Remarks", translate=True, size=50)
    inspection_id = fields.Many2one('vehicle.health.report')

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(VehicleInteriorCondition, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Vehicle Body Outer Conditions
class VehicleOuterCondition(models.Model):
    """Vehicle Condition Line"""
    _name = "vehicle.outer.condition"
    _description = __doc__
    _rec_name = 'vehicle_view'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','exterior')]")
    service_ids = fields.Many2many(comodel_name='product.product', relation='outer_product_rel',
                                   column1='outer_part_id', column2='outer_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Outer Condition Service")
    part_ids = fields.One2many(comodel_name='outer.condition.parts',
                               inverse_name='condition_id',
                               string="Outer Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='exterior.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    vehicle_view = fields.Selection([('top', "Top View"),
                                     ('bottom', "Bottom View"),
                                     ('left_side', "Left Side View"),
                                     ('right_side', "Right Side View"),
                                     ('front', "Front View"),
                                     ('back', "Back View")],
                                    string="Vehicle View")
    vehicle_condition_location_id = fields.Many2one('vehicle.condition.location', string="Location")
    vehicle_condition_id = fields.Many2one('vehicle.condition', string="Condition")
    condition_code = fields.Char(string="Condition Code")
    inspection_id = fields.Many2one('vehicle.health.report')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(VehicleOuterCondition, self).create(vals_list)
        return res

    @api.onchange('vehicle_condition_id')
    def get_condition_description(self):
        for rec in self:
            if rec.vehicle_condition_id:
                rec.condition_code = rec.vehicle_condition_id.condition_code

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Mechanical Conditions
class MechanicalConditionLine(models.Model):
    """Mechanical Item Condition"""
    _name = "mechanical.condition.line"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','under_hood')]")
    service_ids = fields.Many2many(comodel_name='product.product',
                                   relation='mechanical_product_rel',
                                   column1='mechanical_part_id', column2='mechanical_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Mechanical Service")
    part_ids = fields.One2many(comodel_name='mechanical.condition.parts',
                               inverse_name='condition_id',
                               string="Mechanical Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='under.hood.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name",
                                      domain="[('item_category', '=', 'mechanical')]")
    mechanical_condition = fields.Selection([('poor', "Poor"),
                                             ('average', "Average"),
                                             ('not_working', "Not Working"),
                                             ('good', "Good"),
                                             ('other', "Other")],
                                            string="Condition")
    mechanical_condition_notes = fields.Char(string="Remarks", translate=True, size=50)
    inspection_id = fields.Many2one('vehicle.health.report')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(MechanicalConditionLine, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Vehicle Components
class VehicleComponentsLines(models.Model):
    """Vehicle Components"""
    _name = "vehicle.components.line"
    _description = "Multi-Point Inspection"
    _rec_name = 'vehicle_component_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','multi_point')]")
    service_ids = fields.Many2many(comodel_name='product.product',
                                   relation='components_product_rel',
                                   column1='components_part_id', column2='components_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Multi-Point Service")
    part_ids = fields.One2many(comodel_name='components.condition.parts',
                               inverse_name='condition_id',
                               string="Multi-Point Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='multipoint.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    vehicle_component_id = fields.Many2one('vehicle.component', string="Component")
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")],
                                 string="Present Condition")
    remarks = fields.Char(string="Remarks", translate=True, size=50)
    inspection_id = fields.Many2one('vehicle.health.report')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()
    c_vehicle_side = fields.Selection([('top_side', "Top Side"),
                                       ('bottom_side', "Bottom Side")],
                                      string="Vehicle Side")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(VehicleComponentsLines, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Vehicle Fluids
class VehicleFluidsLine(models.Model):
    """Vehicle Fluids"""
    _name = "vehicle.fluids.line"
    _description = __doc__
    _rec_name = 'vehicle_fluid_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','fluid')]")
    service_ids = fields.Many2many(comodel_name='product.product', relation='fluid_product_rel',
                                   column1='fluid_part_id', column2='fluid_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Fluid Service")
    part_ids = fields.One2many(comodel_name='fluid.condition.parts', inverse_name='condition_id',
                               string="Fluid Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='fluid.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    vehicle_fluid_id = fields.Many2one('vehicle.fluid', string="Fluid",
                                       domain="[('fluid_vehicle_side', '=', f_vehicle_side)]")
    f_vehicle_side = fields.Selection([('top_side', "Top Side"),
                                       ('bottom_side', "Bottom Side")],
                                      string="Vehicle Side")
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")],
                                 string="Present Condition")
    remarks = fields.Char(string="Remarks", translate=True, size=50)
    inspection_id = fields.Many2one('vehicle.health.report')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(VehicleFluidsLine, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Under Vehicle
class UnderVehicleInspectionLine(models.Model):
    """Tyre Inspection"""
    _name = 'under.vehicle.inspection.line'
    _description = __doc__
    _rec_name = 'part_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','under_vehicle')]")
    inspection_id = fields.Many2one('vehicle.health.report')
    service_ids = fields.Many2many(comodel_name='product.product',
                                   relation='under_vehicle_product_rel',
                                   column1='under_vehicle_part_id',
                                   column2='under_vehicle_product_id',
                                   domain="[('detailed_type','=','service')]", string="Service")
    part_ids = fields.One2many(comodel_name='under.vehicle.parts', inverse_name='condition_id',
                               string="Under Vehicle Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='under.vehicle.images', inverse_name='inspection_id')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(UnderVehicleInspectionLine, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Tyres Inspections
class TyreInspectionLine(models.Model):
    """Tyre Inspection"""
    _name = 'tyre.inspection.line'
    _description = __doc__
    _rec_name = 'tyre'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','tyre')]")
    service_ids = fields.Many2many(comodel_name='product.product', relation='tyre_product_rel',
                                   column1='tyre_part_id', column2='tyre_product_id',
                                   domain="[('detailed_type','=','service')]",
                                   string="Tyre Service")
    part_ids = fields.One2many(comodel_name='tyre.condition.parts', inverse_name='condition_id',
                               string="Tyre Parts")
    incoming = fields.Char(string="Incoming")
    adjust_to = fields.Char(string="Adjusted To")
    tread_depth = fields.Char(string="Tread Depth")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='tyre.images', inverse_name='inspection_id')

    # Detailed Inspection
    is_detailed_inspection = fields.Boolean(string="Detailed Inspection ?")
    tyre = fields.Selection([('lf', "Left Front"),
                             ('rf', "Right Front"),
                             ('lr', "Left Rear"),
                             ('rr', "Right Rear")],
                            string="Tyre Location")
    tread_wear = fields.Char(string="Tread Wear", translate=True)
    tyre_pressure = fields.Char(string="Tyre Pressure", translate=True)
    brake_pads = fields.Float(string="Brake pads (%)")
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")],
                                 string="Present Condition")
    inspection_id = fields.Many2one('vehicle.health.report')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(TyreInspectionLine, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# Brake Conditions
class BrakeConditionLine(models.Model):
    """Tyre Inspection"""
    _name = 'brake.condition.line'
    _description = __doc__
    _rec_name = 'part_id'

    access_token = fields.Char()
    part_id = fields.Many2one('vehicle.part.info', domain="[('type','=','brake')]")
    inspection_id = fields.Many2one('vehicle.health.report')
    service_ids = fields.Many2many(comodel_name='product.product',
                                   relation='brake_condition_product_rel',
                                   column1='brake_condition_part_id',
                                   column2='brake_condition_product_id',
                                   domain="[('detailed_type','=','service')]", string="Service")
    part_ids = fields.One2many(comodel_name='brake.condition.parts', inverse_name='condition_id',
                               string="Brake Condition Parts")
    required_attention = fields.Boolean()
    further_attention = fields.Boolean()
    okay_for_now = fields.Boolean()
    notes = fields.Text()
    image_ids = fields.One2many(comodel_name='brake.images', inverse_name='inspection_id')

    # Video Details
    inspection_video = fields.Binary()
    file_name = fields.Char()

    # Is Technician User
    is_technician_user = fields.Boolean(related="inspection_id.is_technician_user")

    # DEPRECATED FIELDS
    avatar = fields.Binary()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = secrets.token_urlsafe(16)
            vals['access_token'] = str(token.replace('-', ''))
        res = super(BrakeConditionLine, self).create(vals_list)
        return res

    def action_inspection_button(self):
        return

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False


# -------------------------Inspection Conditions Parts-----------------------------
# Inner Conditions Parts
class InnerConditionsParts(models.Model):
    """Inner Conditions Parts"""
    _name = 'inner.condition.parts'
    _description = "Vehicle Inner Condition Parts"
    _rec_name = 'display_name'

    condition_id = fields.Many2one('vehicle.interior.condition')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Outer Conditions Parts
class OuterConditionsParts(models.Model):
    """Outer Conditions Parts"""
    _name = 'outer.condition.parts'
    _description = "Vehicle Outer Condition Parts"

    condition_id = fields.Many2one('vehicle.outer.condition')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Mechanical Conditions Parts
class MechanicalConditionsParts(models.Model):
    """Mechanical Conditions Parts"""
    _name = 'mechanical.condition.parts'
    _description = "Vehicle Mechanical Condition Parts"

    condition_id = fields.Many2one('mechanical.condition.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Components Conditions Parts
class ComponentsConditionsParts(models.Model):
    """Components Conditions Parts"""
    _name = 'components.condition.parts'
    _description = "Multi-Point Inspection Parts"

    condition_id = fields.Many2one('vehicle.components.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Fluid Conditions Parts
class FluidConditionsParts(models.Model):
    """Fluid Conditions Parts"""
    _name = 'fluid.condition.parts'
    _description = "Vehicle Fluid Condition Parts"

    condition_id = fields.Many2one('vehicle.fluids.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Tyre Conditions Parts
class TyreConditionsParts(models.Model):
    """Tyre Conditions Parts"""
    _name = 'tyre.condition.parts'
    _description = "Vehicle Tyre Condition Parts"
    _rec_name = 'product_id'

    condition_id = fields.Many2one('tyre.inspection.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# Under Vehicle Parts
class UnderVehicleParts(models.Model):
    """Tyre Conditions Parts"""
    _name = 'under.vehicle.parts'
    _description = "Vehicle Under Parts"
    _rec_name = 'product_id'

    condition_id = fields.Many2one('under.vehicle.inspection.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids", string="Services")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


#  Brake Conditions Parts
class BrakeConditionParts(models.Model):
    """Tyre Conditions Parts"""
    _name = 'brake.condition.parts'
    _description = "Brake Condition Part"
    _rec_name = 'product_id'

    condition_id = fields.Many2one('brake.condition.line')
    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty = fields.Float(string="Qty.", default=1.0)
    service_ids = fields.Many2many(related="condition_id.service_ids", string="Services")
    service_id = fields.Many2one('product.product', string="Service",
                                 domain="[('id','in',service_ids)]")
    service_line_id = fields.Many2one('vehicle.required.services')

    @api.depends('product_id.name', 'qty')
    def _compute_display_name(self):
        for rec in self:
            display_name = rec.display_name
            if rec.product_id:
                display_name = rec.product_id.name + " : " + str(rec.qty)
            rec.display_name = display_name


# -------------------------Inspection Images-----------------------------
# Interior Images
class InteriorImages(models.Model):
    _name = 'interior.images'
    _description = "Interior Images"

    inspection_id = fields.Many2one('vehicle.interior.condition')
    name = fields.Char(string="Title", default="Interior Image")
    avtar = fields.Image(string="Avtar")


# Exterior Images
class ExteriorImages(models.Model):
    _name = 'exterior.images'
    _description = "Exterior Images"

    inspection_id = fields.Many2one('vehicle.outer.condition')
    name = fields.Char(string="Title", default="Exterior Image")
    avtar = fields.Image(string="Avtar")


# Under Hood Images
class UnderHoodImages(models.Model):
    _name = 'under.hood.images'
    _description = "Under Hood Images"

    inspection_id = fields.Many2one('mechanical.condition.line')
    name = fields.Char(string="Title", default="Under Hood Image")
    avtar = fields.Image(string="Avtar")


# Fluid Images
class FluidImages(models.Model):
    _name = 'fluid.images'
    _description = "Fluid Images"

    inspection_id = fields.Many2one('vehicle.fluids.line')
    name = fields.Char(string="Title", default="Fluid Image")
    avtar = fields.Image(string="Avtar")


# Tyre Images
class TyreImages(models.Model):
    _name = 'tyre.images'
    _description = "Tyre Images"

    inspection_id = fields.Many2one('tyre.inspection.line')
    name = fields.Char(string="Title", default='Tyre Image')
    avtar = fields.Image(string="Avtar")


# Under Vehicle Images
class UnderVehicleImages(models.Model):
    _name = 'under.vehicle.images'
    _description = "Under Vehicle Images"

    inspection_id = fields.Many2one('under.vehicle.inspection.line')
    name = fields.Char(string="Title", default="Under Vehicle Image")
    avtar = fields.Image(string="Avtar")


# Brake Images
class BrakeImages(models.Model):
    _name = 'brake.images'
    _description = "Brake Images"

    inspection_id = fields.Many2one('brake.condition.line')
    name = fields.Char(string="Title", default="Brake Image")
    avtar = fields.Image(string="Avtar")


# Multi Point Images
class MultiPointImages(models.Model):
    _name = 'multipoint.images'
    _description = "Multi Point Images"

    inspection_id = fields.Many2one('vehicle.components.line')
    name = fields.Char(string="Title", default="Multi Point Image")
    avtar = fields.Image(string="Avtar")
