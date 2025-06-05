# -*- coding: utf-8 -*-
{
    'name': "Fixed Asset Extension",

    'summary': "new module for fixed asset",

    'description': """
    functionality in Odoo
    """,

    'author': "Rauff Imasdeen",
    'category': 'account',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base','account','account_accountant','account_asset'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'models/account_asset_ext.py', no need
        'data/data.xml',
        'views/account_asset_ext.xml',
        'views/account_assest_code_view.xml',
        
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

