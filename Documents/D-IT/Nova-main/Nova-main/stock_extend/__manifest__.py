# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Stock Extend',
    'version' : '0.1',
    'sequence': 6,
    'category': 'Stock, Car Garage',
    'website' : '',
    'summary' : 'Stock extend for car garage',
    'description' : """
Job Card for car garage.

Main Features
-------------
* Add Car Job Card, Car Delivery, Car Product Stock.
""",
    'depends': [
        'base',
        'mail',
        'stock',
        'garage_car'
    ],
    'data': [
        #'report/report_menu.xml',
        #'report/job_card_template.xml',
        'views/stock_picking_view.xml',
    ],

    'installable': True,
    'application': False,
}
