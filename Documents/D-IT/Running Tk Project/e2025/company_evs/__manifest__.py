# -*- coding: utf-8 -*-
{
    'name': 'Enterprise Accounting Extension',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Advanced Accounting Features for Enterprises',

    'author': 'Rauff M Imasdeen',
    'email': 'rauffmimas@gmail.com',
    'mobile': '+971582878939',

    'depends': ['account_asset', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/asset_sequence.xml',
        'views/company_evs_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False

}