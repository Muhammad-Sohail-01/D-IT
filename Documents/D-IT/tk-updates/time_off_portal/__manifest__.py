# -*- coding: utf-8 -*-
{
    'name': "Time Off Portal",

    'summary': "Portal Access - Time Off Requests",

    'description': """
time-off  for employees - portal user time-off requests, view requests, and time-off balance.
    """,

    'author': "Rauff Imasdeen",
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['base','hr_holidays','website','portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

