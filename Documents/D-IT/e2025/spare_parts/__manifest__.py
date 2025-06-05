# -*- coding: utf-8 -*-
{
    'name': "spare_parts",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly in code
    'depends': ['base', "product", 'sale_management', 'stock', 'purchase', 'fleet','automob_partno'],

    'assets': {
        'web.assets_backend': [
            'automob_partno/static/src/js/lot_serial_visibility.js',
        ],
    },

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/spare_parts.xml',
        'views/lot_serial_no_ext.xml',
        'views/stock_picking_ext.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "license": "OPL-1",
}
