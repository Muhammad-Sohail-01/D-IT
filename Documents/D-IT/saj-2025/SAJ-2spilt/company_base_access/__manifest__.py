# -*- coding: utf-8 -*-
{
    'name': "company_base_access",
    'summary': "Manage company access with company groups",
    'description': """
        This module adds company grouping functionality to manage allowed companies
        for products and partners more efficiently.
    """,
    'author': "Rauff Imasdeen",
    'Email': "rauffmimas@gmail.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        # 'views/res_partner_view.xml',


    ],
    "license": "OPL-1",
}

