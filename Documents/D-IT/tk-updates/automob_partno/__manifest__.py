# -*- coding: utf-8 -*-
{
    'name': "automob_partno",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmail.com",

    # for the full list
    'category': 'Uncategorized',
    'version': '0.8',

    # any module necessary for this one to work correctly in code
    'depends': ['base',"product", 'sale_management','stock','purchase','fleet', 'tk_vehicle_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/views.xml',
        'views/product_product_ext.xml',
        'views/templates.xml',
        'views/view_item_catalog.xml',
        'views/view_sale_tk.xml',
        'views/auto_part_number_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
