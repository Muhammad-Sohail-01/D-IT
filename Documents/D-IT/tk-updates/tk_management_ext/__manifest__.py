# -*- coding: utf-8 -*-
{
    'name': "Tk Management Ext",
    'description': """moduel use for tk inheritance""",
    'summary': "tk inheritance",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '17.0.1.0',
    'author': 'Rauff Imasdeen',
    'category': 'services',
    'company': 'TechKhedut Inc.',
    'maintainer': 'Muhammad Odoo Expert',

    # any module necessary for this one to work correctly
    'depends': ['base', 'tk_vehicle_management', 'hr','hr_employee_ext','project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_inherit.xml',
        'views/tk_inspection_views_inherit.xml',
        'views/templates.xml',
        'views/tk_inspection_team_form_view_inherit.xml',
        'views/vehicle_bay.xml',
        'wizard/assign_team_view_inherit.xml'


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'license': 'LGPL-3',

   
}



















