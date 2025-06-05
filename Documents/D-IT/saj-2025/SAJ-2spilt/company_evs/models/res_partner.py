from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_type_affiliate = fields.Boolean(string='Affiliate')
    contact_type_employee = fields.Boolean(string='Employee', compute="_compute_contact_type_employee",store=True)
    contact_type_sale_associate = fields.Boolean(string='Sales Partner')
    contact_type_insurance = fields.Boolean(string='Insurance')

    @api.depends('employee_ids')
    def _compute_contact_type_employee(self):
        for partner in self:
            if partner.employee_ids:
                partner.write({'contact_type_employee': True})
