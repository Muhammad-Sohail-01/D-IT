# -*- coding: utf-8 -*-
# from odoo import http


# class TkManagementExt(http.Controller):
#     @http.route('/tk_management_ext/tk_management_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tk_management_ext/tk_management_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tk_management_ext.listing', {
#             'root': '/tk_management_ext/tk_management_ext',
#             'objects': http.request.env['tk_management_ext.tk_management_ext'].search([]),
#         })

#     @http.route('/tk_management_ext/tk_management_ext/objects/<model("tk_management_ext.tk_management_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tk_management_ext.object', {
#             'object': obj
#         })

