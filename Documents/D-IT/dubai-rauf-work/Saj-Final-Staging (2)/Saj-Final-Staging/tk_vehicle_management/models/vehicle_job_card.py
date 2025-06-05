from odoo import fields, api, models, _


# DEPRECATED
class VehicleJobCard(models.Model):
    _name = 'vehicle.job.card'
    _description = 'Vehicle Job Card'
    _rec_name = 'inspection_id'

    # Inspection Details
    inspection_id = fields.Many2one('vehicle.inspection', string="Vehicle Inspection")

    # Team Details
    team_id = fields.Many2one('inspection.team', string="Team")
    team_leaders_ids = fields.Many2many(related="team_id.team_leader_ids", string="Team Leaders ")
    team_technician_ids = fields.Many2many(related="team_id.technician_ids", string="Team Technicians")
    leaders_ids = fields.Many2many('res.users', string="Team Leaders", domain="[('id','in',team_leaders_ids)]")
    technician_ids = fields.Many2many('res.users', 'vjc_technician_rel', 'vjc_technician_id',
                                      'vjc_user_technician_id', string="Technicians",
                                      domain="[('id','in',team_technician_ids)]")

    # Responsible
    sale_person_id = fields.Many2one(related="inspection_id.sale_person_id", string="Receptionist", store=True)
    service_adviser_id = fields.Many2one(related="inspection_id.service_adviser_id", string="Service Advisor",
                                         store=True)

    # Vehicle Details
    brand_id = fields.Many2one(related="inspection_id.brand_id", string="Vehicle Brand")
    vehicle_model_id = fields.Many2one(related="inspection_id.vehicle_model_id", string="Model", )
    fuel_type = fields.Selection(related="inspection_id.fuel_type", string='Fuel Type')
    transmission = fields.Selection(related="inspection_id.transmission")
    vin_no = fields.Char(related="inspection_id.vin_no", string="VIN No.")
    registration_no = fields.Char(related="inspection_id.registration_no", string="Registration No")
    milage = fields.Char(related="inspection_id.milage", string="Milage")
    miles = fields.Integer(related="inspection_id.miles", string="Kilometers")
    year = fields.Char(related="inspection_id.year", string="Year")
    color = fields.Char(related="inspection_id.color", string="Color")
    is_warranty = fields.Boolean(related="inspection_id.is_warranty", string="Warranty")
    warranty_type = fields.Selection(related="inspection_id.warranty_type", string="Type of Warranty")
    insurance_provider = fields.Char(related="inspection_id.insurance_provider", string="Insurance Provider")
