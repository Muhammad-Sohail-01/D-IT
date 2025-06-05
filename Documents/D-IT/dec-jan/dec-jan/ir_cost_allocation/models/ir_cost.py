from odoo import fields, models, api


class IrCost(models.Model):
    _inherit = "account.move.line"
    # _description = "Cost Allocation"

    contacts_id = fields.Many2one('hr.employee', string="Contacts")
    cost_vehicle = fields.Many2one('register.vehicle', string="Cost - Vehicle")
    
