# -*- coding: utf-8 -*-
{
    'name': 'Insurance Invoice',
    'version': '17.0.1.0.3',
    'category': 'Sales',
    'summary': 'Sales Order spliting for insurance and customer Invoice',
    'description': "Sales order "
                   "Accounts Invoice.",
    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmailcom",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_order_insurance_inherit.xml',
        'wizard/sale_create_payment_wizard_inherit.xml',
        'wizard/res_configuration_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "license": "OPL-1",
}

