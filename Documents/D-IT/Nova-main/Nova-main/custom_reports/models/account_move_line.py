from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    line_name = fields.Text(string='Name', compute="_compute_line_name")

    @api.depends('name')
    def _compute_line_name(self):
        """Compute method to assign label field into line name field
        in order to get that into the report as a text field"""
        for record in self:
            if record.name:
                record.line_name = record.name
            else:
                record.line_name = False
