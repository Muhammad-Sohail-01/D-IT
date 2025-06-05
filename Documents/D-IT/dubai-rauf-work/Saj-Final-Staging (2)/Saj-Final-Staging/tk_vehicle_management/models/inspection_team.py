from odoo import api, fields, models


class InspectionTeam(models.Model):
    _name = 'inspection.team'
    _description = 'Inspection Team'

    name = fields.Char(string="Name")
    team_leader_ids = fields.Many2many('res.users', string="Team Leaders",
                                       domain=lambda self: [('groups_id', '=', self.env.ref(
                                           'tk_vehicle_management.vehicle_team_leader').id)])
    technician_ids = fields.Many2many('res.users', 'team_technician_rel', 'technician_id', 'technician_user_id',
                                      string='Technicians', domain=lambda self: [
            ('groups_id', '=', self.env.ref('tk_vehicle_management.vehicle_technician').id)])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(InspectionTeam, self).create(vals_list)
        for rec in res:
            for data in rec.team_leader_ids:
                ids = data.inspection_team_ids.ids
                ids.append(rec.id)
                data.inspection_team_ids = [(6, 0, ids)]
            for data in rec.technician_ids:
                technician_team_ids = data.inspection_team_ids.ids
                technician_team_ids.append(rec.id)
                data.inspection_team_ids = [(6, 0, technician_team_ids)]
        return res

    def write(self, vals):
        res = super(InspectionTeam, self).write(vals)
        return res


class UserInspectionTeam(models.Model):
    _inherit = 'res.users'

    inspection_team_ids = fields.Many2many('inspection.team', string="Teams")
