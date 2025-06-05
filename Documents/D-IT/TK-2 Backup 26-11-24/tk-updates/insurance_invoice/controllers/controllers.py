# -*- coding: utf-8 -*-
# from odoo import http


# class InsuranceInvoice(http.Controller):
#     @http.route('/insurance_invoice/insurance_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/insurance_invoice/insurance_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('insurance_invoice.listing', {
#             'root': '/insurance_invoice/insurance_invoice',
#             'objects': http.request.env['insurance_invoice.insurance_invoice'].search([]),
#         })

#     @http.route('/insurance_invoice/insurance_invoice/objects/<model("insurance_invoice.insurance_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('insurance_invoice.object', {
#             'object': obj
#         })

