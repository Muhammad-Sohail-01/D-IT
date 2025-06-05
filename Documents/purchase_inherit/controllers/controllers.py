# -*- coding: utf-8 -*-
# from odoo import http
# from odoo.http import request
#
# class YourController(http.Controller):
#
#     @http.route('/your/model/confirm_action', type='http', auth="user", website=True)
#     def confirm_action(self, **kw):
#         # Perform your state confirmation logic here
#         record_id = int(kw.get('record_id', 0))
#         if record_id:
#             record = request.env['community.purchase'].browse(record_id)
#             record.write({'state': 'confirm'})
#
#         # Redirect to the first menu of the model
#         return request.redirect('/web#menu_id=purchase.menu_purchase_form_action')
