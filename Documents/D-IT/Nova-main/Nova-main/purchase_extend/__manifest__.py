# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Extend',
    'version' : '0.1',
    'sequence': 6,
    'category': 'Purchase, Car Garage',
    'website' : '',
    'summary' : 'Purchase extend for car garage',
    'description' : """

Main Features
-------------
* Purchase Car row materials.
""",
    'depends': [
        'mail',
        'purchase',
    ],
    'data': [
        'views/purchase_order_view.xml',

    ],

    'installable': True,
    'application': False,
}
