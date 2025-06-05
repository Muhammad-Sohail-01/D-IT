from odoo import api, fields, models


class VehicleFleet(models.Model):
    _inherit = 'fleet.vehicle'

    # Count
    booking_count = fields.Integer(string="Check in Count", compute="compute_count")
    job_card_count = fields.Integer(string="Job Card Count", compute="compute_count")
    inspection_count = fields.Integer(string="Inspection Count", compute="compute_count")

    def compute_count(self):
        for rec in self:
            rec.booking_count = self.env['vehicle.booking'].search_count([('fleet_id', '=', rec.id)])
            rec.job_card_count = 0
            rec.inspection_count = self.env['vehicle.inspection'].search_count([('fleet_id', '=', rec.id)])

    def action_view_job_card(self):
        return

    def action_view_bookings(self):
        return {
            "name": "Check ins",
            "type": "ir.actions.act_window",
            "domain": [("fleet_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": 'vehicle.booking',
            "target": "current",
        }

    def action_view_inspection(self):
        return {
            "name": "Vehicle Job Card",
            "type": "ir.actions.act_window",
            "domain": [("fleet_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": 'vehicle.inspection',
            "target": "current",
        }
