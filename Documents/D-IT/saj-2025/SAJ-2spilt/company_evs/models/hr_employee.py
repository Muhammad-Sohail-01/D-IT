from odoo import models, fields, api


# class HrEmployee (models.Model):
#     _inherit = 'hr.employee'
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         employees = super().create (vals_list)
#
#         for employee in employees:
#             # Update the related partner record
#             if employee.address_home_id:
#                 employee.address_home_id.write ({
#                     'contact_type_employee': True
#                 })
#             # If no partner exists, create one
#             else:
#                 partner_vals = {
#                     'name': employee.name,
#                     'contact_type_employee': True,
#                     'type': 'private'
#                 }
#                 partner = self.env['res.partner'].create (partner_vals)
#                 employee.write ({'address_home_id': partner.id})
#
#         return employees
#
#     def write(self, vals):
#         res = super ().write (vals)
#
#         # If home address is being changed/set
#         if vals.get ('address_home_id'):
#             self.env['res.partner'].browse (vals['address_home_id']).write ({
#                 'contact_type_employee': True
#             })
#
#         return res