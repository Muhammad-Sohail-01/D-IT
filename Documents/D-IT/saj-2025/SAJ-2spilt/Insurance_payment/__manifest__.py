# -*- coding: utf-8 -*-
{
    'name': "Insurance Payment",
    'version': '17.1',
    'category': 'Accounting/Insurance',
    'summary': 'Manage Insurance Payments in Odoo',
    'description': """
        This module adds functionality to handle insurance payments within Odoo.
    """,
    'author': "Rauff M Imasdeen",
    'email': "rauffmimas@gmail.com",
    'depends': ['base', 'account','sale','sale_management','tk_vehicle_management', 'company_evs'],
    'data': [
        'security/ir.model.access.csv',
        'views/insurance_payment_views.xml',
        'views/res_partner_views.xml',
    ],
'images': [
    'static/description/icon.png',
    'static/description/whatsapp-icon.png',
    'static/description/logo.png',
    'static/description/banner.png',
],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}