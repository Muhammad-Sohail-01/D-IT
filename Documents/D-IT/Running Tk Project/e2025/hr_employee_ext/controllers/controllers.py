# -*- coding: utf-8 -*-
# from odoo import http


# class HrEmployeeExt(http.Controller):
#     @http.route('/hr_employee_ext/hr_employee_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_employee_ext/hr_employee_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_employee_ext.listing', {
#             'root': '/hr_employee_ext/hr_employee_ext',
#             'objects': http.request.env['hr_employee_ext.hr_employee_ext'].search([]),
#         })

#     @http.route('/hr_employee_ext/hr_employee_ext/objects/<model("hr_employee_ext.hr_employee_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_employee_ext.object', {
#             'object': obj
#         })

