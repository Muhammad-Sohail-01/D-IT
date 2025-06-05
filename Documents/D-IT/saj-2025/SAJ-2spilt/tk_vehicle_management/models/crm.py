from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class VehicleCRM(models.Model):
    _inherit = 'crm.lead'

    booking_id = fields.Many2one('vehicle.booking', string="Vehicle Check in")
    vehicle_concern_ids = fields.One2many('crm.booking.concern', 'lead_id', string="Consent")

    # Customer Details
    address_area = fields.Char(string="Address/Area")
    customer_tag_ids = fields.Many2many('customer.tags', string="Tag")

    # Vehicle Details
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
    vehicle_color = fields.Selection([
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
                                      ('extended_evs', 'Extended With EVS')], string="Type of Warranty")
    insurance_provider = fields.Char(string="Insurance Provider")
    licence_image_front = fields.Image(string="Licence Image Front")
    licence_image_back = fields.Image(string="Licence Image Back")

    # Check in Details
    booking_date = fields.Date(string="Check in Date", default=fields.Date.today)
    booking_source = fields.Selection([('direct', "Direct"),
                                       ('website', "Website")],
                                      string="Check in Source", default='direct')

    # Count
    invoice_count = fields.Integer(string="Invoice Count", compute="compute_count")
    do_count = fields.Integer(string="Parts Order Count", compute="compute_count")

    # Deprecated
    last_name = fields.Char(string="Last Name")
    milage = fields.Char(string="Mileage")

    # Service Adviser & Technician
    service_adviser_id = fields.Many2one(comodel_name='res.users', string="Service Advisor",
                                         domain=lambda self: [('groups_id', '=', self.env.ref(
                                             'tk_vehicle_management.vehicle_service_adviser').id)])

    technician_id = fields.Many2one('res.users', string="Technician",
                                    domain=lambda self: [('groups_id', '=', self.env.ref(
                                        'tk_vehicle_management.vehicle_technician').id)])

    vehicle_appointment_id = fields.Many2one('calendar.event', string="Vehicle Appointment")

    # Constrain
    @api.constrains('vin_no')
    def _check_vin_no_length(self):
        for record in self:
            if record.vin_no and not len(record.vin_no) == 17:
                raise ValidationError("VIN No should be 17 characters long.")

    # Compute
    @api.depends('booking_id')
    def compute_count(self):
        for rec in self:
            count = 0
            do_count = 0
            if rec.booking_id.inspection_id:
                count = self.env['account.move'].search_count([('job_card_id', '=', rec.booking_id.inspection_id.id)])
                do_count = self.env['stock.picking'].search_count(
                    [('job_card_id', '=', rec.booking_id.inspection_id.id),
                     ('picking_type_code', 'in', ['outgoing', 'incoming'])])
            rec.invoice_count = count
            rec.do_count = do_count

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        """ Extract data from lead to create a partner.

        :param name : furtur name of the partner
        :param is_company : True if the partner is a company
        :param parent_id : id of the parent partner (False if no parent)

        :return: dictionary of values to give at res_partner.create()
        """
        email_parts = tools.email_split(self.email_from)
        res = {
            'name': partner_name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_parts[0] if email_parts else False,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'is_company': is_company,
            'type': 'contact'
        }
        if self.lang_id.active:
            res['lang'] = self.lang_id.code
        if self.address_area:
            res['address_area'] = self.address_area
        return res

    def action_create_booking(self):
        concern_lines = []
        record = {
            'customer_id': self.partner_id.id,
            'address_area': self.partner_id.address_area,
            'brand_id': self.brand_id.id,
            'vehicle_model_id': self.vehicle_model_id.id,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'vin_no': self.vin_no,
            'registration_no': self.registration_no,
            'miles': self.miles,
            'year': self.year,
            'color': self.vehicle_color,
            'is_warranty': self.is_warranty,
            'warranty_type': self.warranty_type,
            'insurance_provider': self.insurance_provider,
            'lead_id': self.id,
            'customer_tag_ids': self.customer_tag_ids.ids,
            'booking_source': 'lead',
            'lead_source_id': self.source_id.id,
            'lead_medium_id': self.medium_id.id,
            'licence_image_front': self.licence_image_front,
            'licence_image_back': self.licence_image_back,
            'service_adviser_id': self.service_adviser_id.id,
        }
        for data in self.vehicle_concern_ids:
            concern_lines.append((0, 0, {
                'name': data.name,
                'display_type': data.display_type,
                'sequence': data.sequence,
                'concern_type_id': data.concern_type_id.id,
            }))
        record['vehicle_concern_ids'] = concern_lines
        booking_id = self.env['vehicle.booking'].create(record)
        self.booking_id = booking_id.id
        self.booking_id.action_send_booking_whatsapp_message(send_to='service_adviser')
        self.booking_id.action_send_booking_whatsapp_message(send_to='customer')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicle Check in'),
            'res_model': 'vehicle.booking',
            'res_id': booking_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_bookings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicle Check in'),
            'res_model': 'vehicle.booking',
            'res_id': self.booking_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_job_card(self):
        if not self.booking_id.inspection_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Job-card is not created yet !'),
                    'sticky': False,
                }}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Job Card'),
            'res_model': 'vehicle.inspection',
            'res_id': self.booking_id.inspection_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_inspection(self):
        if not self.booking_id.inspection_id.vehicle_health_report_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Vehicle job card report is not created yet !'),
                    'sticky': False,
                }}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Report'),
            'res_model': 'vehicle.health.report',
            'res_id': self.booking_id.inspection_id.vehicle_health_report_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_view_invoices(self):
        if not self.booking_id.inspection_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Job-card is not created yet !'),
                    'sticky': False,
                }}
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('job_card_id', '=', self.booking_id.inspection_id.id)],
            'context': {'default_job_card_id': self.booking_id.inspection_id.id, 'default_move_type': 'out_invoice'},
            'view_mode': 'tree,kanban,form',
            'target': 'current'
        }
        return action

    def action_view_activities(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activity',
            'res_model': 'crm.lead',
            'domain': [('id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'activity',
            'target': 'current'
        }

    def action_view_delivery_orders(self):
        if not self.booking_id.inspection_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Job-card is not created yet !'),
                    'sticky': False,
                }}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parts Orders',
            'res_model': 'stock.picking',
            'domain': [('job_card_id', '=', self.booking_id.inspection_id.id),
                       ('picking_type_code', 'in', ['outgoing', 'incoming'])],
            'context': {'create': False},
            'view_mode': 'tree,kanban,form',
            'target': 'current'
        }


class CRMBookingConcern(models.Model):
    _name = 'crm.booking.concern'
    _description = "CRM Check in Consent"

    lead_id = fields.Many2one('crm.lead', string="Lead")
    concern_type_id = fields.Many2one('concern.type', string="Consent", )
    name = fields.Text(string="Description")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ], default=False)
    sequence = fields.Integer()
