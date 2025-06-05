# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Invoice Extend',
    'version': '16.0.0.2',
    'sequence': 7,
    'category': 'Invoice, Car Garage Tax Invoice',
    'website' : '',
    'summary' : 'Invoice extend for car garage',
    'description' : """

Main Features
-------------
* Add Car Tax Invoice, Car Warranty details, Car Completion pictures and Car out time.
""",
    'depends': [
        'base',
        'mail',
        'account',
        'garage_car'
    ],
    'data': [
        'security/ir.model.access.csv',
        #'data/report_paperformat.xml',
        #'report/invoice_report_menu.xml',
        #'report/invoice_report_template.xml',
        #'report/report_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/invoice_view.xml',
        'views/car_service_view.xml',
    ],

    'installable': True,
    'application': False,
}
