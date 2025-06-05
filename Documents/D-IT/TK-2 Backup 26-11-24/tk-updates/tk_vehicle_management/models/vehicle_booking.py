from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleBooking(models.Model):
    _name = 'vehicle.booking'
    _description = 'Vehicle Check in'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Check in Details
    name = fields.Char(string='Check in No', default=lambda self: _('New'), copy=False)
    vehicle_from = fields.Selection([('new', "New"),
                                     ('customer_vehicle', "Vehicle From Customer")],
                                    string="Vehicle From", default='customer_vehicle')
    lead_id = fields.Many2one('crm.lead', string="Lead")
    inspection_id = fields.Many2one('vehicle.inspection', string="Inspection")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    status = fields.Selection([('check_in', 'Check in'), ('job_card', 'Job Card')],
                              default='check_in')

    # Customer Details
    customer_id = fields.Many2one('res.partner', string="Customer")
    last_name = fields.Char(string="Last Name")  # Deprecated
    email = fields.Char(string="Email", related="customer_id.email")
    phone = fields.Char(string="Phone", related="customer_id.phone")
    address_area = fields.Char(related="customer_id.address_area", store=True, readonly=False,
                               string="Address/Area")
    priority = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], string="Priority")
    customer_tag_ids = fields.Many2many('customer.tags', string="Tags")
    notes = fields.Html(string="Notes")
    business = fields.Boolean(string="Business")
    vehicle_concern_ids = fields.One2many('booking.concern', 'booking_id', string="Consent")

    # Vehicle Details
    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    register_vehicle_id = fields.Many2one('register.vehicle', string="Register Vehicle",
                                          domain="[('customer_id','=',customer_id)]")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Vehicle Brand")
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string="Model",
                                       domain="[('brand_id','=',brand_id)]")
    fuel_type = fields.Selection([('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                 'Fuel Type', default='electric')
    transmission = fields.Selection([('manual', 'Manual'),
                                     ('automatic', 'Automatic'),
                                     ('cvt', 'CVT')],
                                    default='automatic')
    vin_no = fields.Char(string="VIN No.")
    registration_no = fields.Char(string="Registration No")
    miles = fields.Integer(string="Kilometers")
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
    is_warranty = fields.Boolean(string="Warranty")
    warranty_type = fields.Selection([('manufacture', 'Manufacture'),
                                      ('extended', 'Extended Warranty'),
                                      ('extended_evs', 'Extended With EVS')],
                                     string="Type of Warranty")
    insurance_provider = fields.Many2one('res.partner',string="Insurance Provider")
    licence_image_front = fields.Image(string="Licence Image Front")
    licence_image_back = fields.Image(string="Licence Image Back")

    # Booking Details
    booking_date = fields.Date(string="Check in Date", default=fields.Date.today)
    booking_source = fields.Selection([('direct', "Direct"),
                                       ('website', "Website"), ('lead', 'Lead'),
                                       ('other', 'Other')],
                                      string="Check in Source", default='direct')
    lead_source_id = fields.Many2one('utm.source', string="Lead Source")
    lead_medium_id = fields.Many2one('utm.medium', string="Lead Medium")
    other_source = fields.Char(string="Source")

    # Responsible
    sale_person_id = fields.Many2one('res.users', string="Receptionist",
                                     default=lambda
                                         self: self.env.user and self.env.user.id or False)
    service_adviser_id = fields.Many2one('res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])

    # Warranty
    warranty_contract_id = fields.Many2one('vehicle.warranty', string="Warranty Contract")

    # Appoint Details
    vehicle_appointment_id = fields.Many2one('calendar.event', string="Appointment")

    # DEPRECATED
    milage = fields.Char(string="Mileage")

    # Methods : Create
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.booking') or _('New')
        return super(VehicleBooking, self).create(vals_list)

    # Constrain
    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    # Onchange
    @api.onchange('customer_id')
    def onchange_customer_info(self):
        for rec in self:
            rec.last_name = rec.customer_id.lastname
            rec.address_area = rec.customer_id.address_area

    @api.onchange('fleet_id', 'vehicle_from', 'register_vehicle_id')
    def onchange_vehicle_info(self):
        for rec in self:
            if rec.register_vehicle_id and rec.vehicle_from == 'customer_vehicle':
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

    def process_vehicle_value(self, register_vehicle_id, miles):
        """Process Register Vehicle Details"""
        self.write({
            'register_vehicle_id': register_vehicle_id,
            'vehicle_from': 'customer_vehicle',
            'miles': miles
        })
        self.onchange_vehicle_info()

    @api.onchange('register_vehicle_id', 'vehicle_from', 'booking_date')  # Check Warranty
    def _onchange_warranty_contract_id(self):
        for rec in self:
            if rec.register_vehicle_id and rec.vehicle_from == 'customer_vehicle':
                warranty_contract_id = self.env['vehicle.warranty'].search(
                    [('register_vehicle_id', '=', rec.register_vehicle_id.id),
                     ('status', '=', 'running'),
                     ('start_date', '<=', rec.booking_date),
                     ('end_date', '>=', rec.booking_date)], limit=1)
                if warranty_contract_id:
                    rec.warranty_contract_id = warranty_contract_id.id

    # Button
    def action_register_vehicle(self):
        """Register Vehicle when new vehicle"""
        register_vehicle_id = self.env['register.vehicle'].sudo().create({
            'customer_id': self.customer_id.id,
            'brand_id': self.brand_id.id,
            'vehicle_model_id': self.vehicle_model_id.id,
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'year': self.year,
            'color': self.color,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'insurance_provider': self.insurance_provider,
            'warranty_type': self.warranty_type,
            'is_warranty': self.is_warranty,
        })
        self.write({
            'vehicle_from': 'customer_vehicle',
            'register_vehicle_id': register_vehicle_id.id,
        })

    def action_create_vehicle_inspection(self):
        if not self.register_vehicle_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Vehicle Missing'),
                    'message': _('Please add Vehicle !'),
                    'sticky': False,
                }}
        concern_line = []
        if not self.service_adviser_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Add 'Service Advisor' to Create Inspection"),
                    'sticky': False,
                    'type': "info",
                }
            }
        booking_record = {'vehicle_from': self.vehicle_from,
                          'lead_id': self.lead_id.id,
                          'customer_id': self.customer_id.id,
                          'last_name': self.last_name,
                          'address_area': self.address_area,
                          'priority': self.priority,
                          'customer_tag_ids': self.customer_tag_ids.ids,
                          'notes': self.notes,
                          'business': self.business,
                          'fleet_id': self.fleet_id.id,
                          'register_vehicle_id': self.register_vehicle_id.id,
                          'vehicle_model_id': self.vehicle_model_id.id,
                          'brand_id': self.brand_id.id,
                          'fuel_type': self.fuel_type,
                          'transmission': self.transmission,
                          'vin_no': self.vin_no,
                          'registration_no': self.registration_no,
                          'miles': self.miles,
                          'year': self.year,
                          'color': self.color,
                          'is_warranty': self.is_warranty,
                          'warranty_type': self.warranty_type,
                          'insurance_provider': self.insurance_provider,
                          'licence_image_front': self.licence_image_front,
                          'licence_image_back': self.licence_image_back,
                          'booking_date': self.booking_date,
                          'booking_source': self.booking_source,
                          'lead_source_id': self.lead_source_id.id,
                          'lead_medium_id': self.lead_medium_id.id,
                          'other_source': self.other_source,
                          'service_adviser_id': self.service_adviser_id.id,
                          # Warranty
                          'warranty_contract_id': self.warranty_contract_id.id,
                          'booking_id': self.id,
                          # From Check-In
                          'is_check_in_create': True
                          }
        for data in self.vehicle_concern_ids:
            concern_line.append((0, 0, {
                'name': data.name,
                'concern_type_id': data.concern_type_id.id,
                'display_type': data.display_type,
                'sequence': data.sequence,
            }))
        booking_record['vehicle_concern_ids'] = concern_line
        inspection_id = self.env['vehicle.inspection'].create(booking_record)
        self.inspection_id = inspection_id.id
        self.status = 'job_card'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Job Card',
            'res_model': 'vehicle.inspection',
            'res_id': inspection_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_job_card(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card',
            'res_model': 'vehicle.inspection',
            'res_id': self.inspection_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    # Send Whatsapp Message
    def action_send_booking_whatsapp_message(self, send_to):
        template_id = False
        partner_id = False
        if send_to == 'customer':
            template_id = 'tk_vehicle_management.wa_check_in_customer_template_id'
            partner_id = self.customer_id
        elif send_to == 'service_adviser':
            template_id = 'tk_vehicle_management.wa_check_in_service_advisor_template_id'
            partner_id = self.service_adviser_id.partner_id
        wa_template_id = self.get_whatsapp_template(template_id=template_id)
        if not wa_template_id:
            return
        mobile_no = self.check_whatsapp_phone(partner_id=partner_id)
        if mobile_no:
            self.action_send_whatsapp_message(mobile_no, wa_template_id)

    def get_whatsapp_template(self, template_id):
        # Get Template from Settings
        wa_template_id = False
        config_template_id = self.env['ir.config_parameter'].sudo().get_param(template_id)
        if config_template_id:
            wa_template_id = self.env['whatsapp.template'].sudo().browse(int(config_template_id))
        return wa_template_id

    def check_whatsapp_phone(self, partner_id):
        # Check WhatsApp Phone No
        mobile_no = False
        if partner_id.mobile:
            mobile_no = partner_id.mobile
        elif partner_id.phone:
            mobile_no = partner_id.phone
        return mobile_no

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
            header_params = wa_template_id.variable_ids.filtered(
                lambda line: line.line_type == 'header')
            if wa_template_id.variable_ids and header_params:
                header_param = header_params[0]
                if header_param.field_type == 'free_text' and not header_text_1:
                    header_text_1 = header_param.demo_value
        # Prepare Body
        template_variables_value = wa_template_id.variable_ids._get_variables_value(rec)
        text_vars = wa_template_id.variable_ids.filtered(lambda var: var.field_type == 'free_text')
        for var_index, body_text_var in zip(range(1, number_of_free_text + 1),
                                            text_vars.filtered(
                                                lambda var: var.line_type == 'body')):
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
        message = self.env['mail.message'].create(
            dict(post_values, res_id=self.id, model=wa_template_id.model,
                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id(
                     "mail.mt_note")))
        message = self.env['whatsapp.message'].sudo().create({
            'mobile_number': phone,
            'wa_template_id': wa_template_id.id,
            'wa_account_id': wa_template_id.wa_account_id.id,
            'mail_message_id': message.id,
        })
        message._send(force_send_by_cron=True)


class BookingConcern(models.Model):
    _name = 'booking.concern'
    _description = "Check in Consent"

    booking_id = fields.Many2one('vehicle.booking', string="Vehicle Check in")
    concern_type_id = fields.Many2one('concern.type', string="Consent", )
    name = fields.Text(string="Description")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ], default=False)
    sequence = fields.Integer()
