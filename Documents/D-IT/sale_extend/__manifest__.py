# -*- coding: utf-8 -*-
{
    'name' : 'Sale Extend',
    'version' : '17.0.0.2',
    'sequence': 10,
    'category': 'Sale, Car Garage',
    'website' : '',
    'summary' : 'Sale extend for car garage',
    'description' : """
I                     n time, Current mileage, Issue fault Main heading, Customer note, Repairing cost and Car damage pictures and card blue print diagramed.

Main Features
-------------
* Add Car in time, Current mileage, Issue fault Main heading and Repairing cost and Car damage pictures and card blue print diagramed.
""",
    'depends': [
        'base',
        'mail',
        'sale',
        'sale_management',
        'hr',
        'garage_car',
        'product',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        #'data/report_paperformat.xml',
        #'report/inspection_report.xml',
        #'report/inspection_report_templates.xml',
        #'report/estimation_report_template.xml',
        #'report/report_sale_view.xml',
        'views/sale_menu_ext.xml'
    ],

    'installable': True,
    'application': False,
}
