# -*- coding: utf-8 -*-

{
    'name': 'Product Pack',
    'version': '17.0.1.0.1',
    'category': 'Sales',
    'summary': 'Multiple Products as Pack',
    'description': """ This module allows to add multiple products as pack.""",
    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmail.com",
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
