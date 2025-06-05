import uuid
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehiclePartner(models.Model):
    _inherit = 'res.partner'
    _rec_names_search = ['phone','mobile','address_area']

    
    address_area = fields.Char(string="Address/Area")
    vehicle_count = fields.Integer(compute="compute_count")

    def compute_count(self):
        for rec in self:
            rec.vehicle_count = self.env['register.vehicle'].sudo().search_count([('customer_id', '=', rec.id)])

    def action_view_register_vehicle(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Vehicles'),
            'res_model': 'register.vehicle',
            'domain': [('customer_id', '=', self.id)],
            'context': {
                'default_customer_id': self.id,
            },
            'view_mode': 'tree,form',
            'target': 'current'
        }

    # Deprecated
    last_name = fields.Char(string="Last Name")


class RegisterVehicle(models.Model):
    """Register Vehicle"""
    _name = 'register.vehicle'
    _description = __doc__
    _rec_name = 'vehicle_model_id'
    _rec_names_search = ['vehicle_model_id', 'vin_no', 'registration_no', 'customer_name']
    _inherit = ['mail.thread', 'mail.activity.mixin']

    access_token = fields.Char(string="Access Token")
    customer_id = fields.Many2one('res.partner', string='Customer', domain="['|', ('category_id', '=', False), ('category_id.name', '!=', 'Employee')]")
    email = fields.Char(string="Email", related="customer_id.email", readonly=False)
    mobile = fields.Char(string="Mobile", related="customer_id.mobile", readonly=False)

    # Vehicle Details
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Vehicle")
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string="Model",
                                       domain="[('brand_id','=',brand_id)]")
    vid_no = fields.Char(string="VID NO")
    registration_no = fields.Char(string="Registration No")
    vin_no = fields.Char(string="VIN Number")
    year = fields.Char(string="Year")
    color = fields.Selection([
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('brown', 'Brown'),
        ('burgundy', 'Burgundy'),
        ('gold', 'Gold'),
        ('grey', 'Grey'),
        ('orange', 'Orange'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('silver', 'Silver'),
        ('beige', 'Beige'),
        ('tan', 'Tan'),
        ('teal', 'Teal'),
        ('white', 'White'),
        ('yellow', 'Yellow'),
        ('other', 'Other Color'),
    ], string="Color")
    fuel_type = fields.Selection([('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                 'Fuel Type', default='electric')
    transmission = fields.Selection([('manual', 'Manual'),
                                     ('automatic', 'Automatic'),
                                     ('cvt', 'CVT')],
                                    default='automatic')
    is_warranty = fields.Boolean(string="Warranty")
    warranty_type = fields.Selection([('manufacture', 'Manufacture'),
                                      ('extended', 'Extended Warranty'),
                                      ('extended_evs', 'Extended With EVS')], string="Type of Warranty")
    # insurance_provider = fields.Char(string="Insurance Provider")
    insurance_provider = fields.Many2one('res.partner', string="Insurance Provider", domain="[('category_id.name', '=', 'Insurance')]")
    policy_number = fields.Char(string="Policy Number")
    insurance_expire_date = fields.Date(string="Insurance Expire Date")

    # Count
    booking_count = fields.Integer(string="Check in Count", compute="compute_count")
    job_card_count = fields.Integer(string="Job Card Count", compute="compute_count")
    inspection_count = fields.Integer(string="Inspection Count", compute="compute_count")
    warranty_count = fields.Integer(string="Warranty Count", compute="compute_count")

    # DEPRECATED
    milage = fields.Char(string="Milage")
    customer_name = fields.Char(string="Customer Name", compute="_compute_customer_name", store=True)
    company_id = fields.Many2one('res.company',  string="Company", default=lambda self: self.env.company)

    _sql_constraints = [
        (
            "unique_vin_no",
            "unique (vin_no)",
            "VIN Number should be unique for Vehicle رقم VIN موجود بالفعل! الرجاء التحقق من تفاصيل تسجيل المركبة"
        ),
    ]

    @api.constrains('vid_no')
    def _check_unique_vid_no(self):
        for record in self:
            if record.vid_no:
                duplicate = self.search([('vid_no', '=', record.vid_no), ('id', '!=', record.id)], limit=1)
                if duplicate:
                    raise ValidationError("VIN Number should be unique for Vehicle رقم VIN موجود بالفعل! الرجاء التحقق من تفاصيل تسجيل المركبة")

    
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.brand_id.name}/{rec.vehicle_model_id.name}[{rec.registration_no}]"

    @api.depends('customer_id')
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_id.name

    
    #update sequence for already created vehicle
    def update_existing_vid_numbers(self):
        records = self.sudo().search([()])
        for record in records:
            company = self.env['res.company'].browse(vals.get('company_id'))
            if not company:
                raise UserError(
                    _("No company present in this vehicle Record : %s") % record.brand
                )

            seq = self.env['ir.sequence'].sudo().next_by_code('vehicle.register.sequence') or '0001'
            record.vid_no = f"V{company.unique_code}{seq}"


           

            

    # ORM : Create / Write / Constrain / Default_get 
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company = self.env['res.company'].browse(vals.get('company_id')) or self.env.company
            seq = self.env['ir.sequence'].next_by_code('vehicle.register.sequence') or '0001'
            unique_code = company.company_custom_id or ''
            vals['access_token'] = str(uuid.uuid4())
            vals['vid_no'] = f"V{unique_code}{seq}"
        return super(RegisterVehicle, self).create(vals_list)

    # Constrain
    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    def compute_count(self):
        for rec in self:
            rec.booking_count = self.env['vehicle.booking'].search_count([('register_vehicle_id', '=', rec.id)])
            rec.job_card_count = 0
            rec.inspection_count = self.env['vehicle.inspection'].search_count([('register_vehicle_id', '=', rec.id)])
            rec.warranty_count = self.env['vehicle.warranty'].search_count([('register_vehicle_id', '=', rec.id)])

    def action_view_job_card(self):
        return

    def action_view_bookings(self):
        return {
            "name": "Check ins",
            "type": "ir.actions.act_window",
            "domain": [("register_vehicle_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": 'vehicle.booking',
            "target": "current",
        }

    def action_view_inspection(self):
        return {
            "name": "Vehicle job Card",
            "type": "ir.actions.act_window",
            "domain": [("register_vehicle_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": 'vehicle.inspection',
            "target": "current",
        }

    def action_view_warranties(self):
        return {
            "name": "Warranties",
            "type": "ir.actions.act_window",
            "domain": [("register_vehicle_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": 'vehicle.warranty',
            "target": "current",
        }

    def action_create_job(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Job'),
            'res_model': 'vehicle.inspection',
            'context': {
                'default_register_vehicle_id': self.id,
                'default_customer_id': self.customer_id.id,
            },
            'view_mode': 'form',
            'target': 'new'
        }

    def get_portal_url(self):
        url = '/my/vehicle/registered-vehicle/form/' + self.access_token
        return url
