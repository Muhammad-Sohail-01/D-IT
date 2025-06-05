from odoo import fields, models, api


class IrCost(models.Model):
    _inherit = "account.move.line"
    # _description = "Cost Allocation"

    contacts_id = fields.Many2one('hr.employee', string="Contacts")
