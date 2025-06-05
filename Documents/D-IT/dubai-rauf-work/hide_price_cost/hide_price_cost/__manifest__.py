# -*- coding: utf-8 -*-
{
    'name': "Hide Cost & Price for Users",
    'summary': """Access control for hide the product price and cost.""",
    'description': """TAccess control for hide the product price and cost""",
    "name": "Hide Cost & Price for Users",

    "author": "Rauff Imasdeen",
    "email": "rauffmimas@gmailcom",
    "mobile": "+971 5828 78 939",
    "version": "17.0",

    'category': 'Sales',
    'version': '17.0.1.2.0',

    'depends': ['base', 'product'],
    'data': [
       'security/hide_price_cost_group.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
    ],


    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
