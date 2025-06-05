# -*- coding: utf-8 -*-
# from odoo import http


# class CompanyBaseAccess(http.Controller):
#     @http.route('/company_base_access/company_base_access', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_base_access/company_base_access/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_base_access.listing', {
#             'root': '/company_base_access/company_base_access',
#             'objects': http.request.env['company_base_access.company_base_access'].search([]),
#         })

#     @http.route('/company_base_access/company_base_access/objects/<model("company_base_access.company_base_access"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_base_access.object', {
#             'object': obj
#         })

