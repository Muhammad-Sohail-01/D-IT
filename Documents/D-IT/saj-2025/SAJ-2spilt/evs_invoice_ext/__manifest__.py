# -*- coding: utf-8 -*-

{
    "name": "EVS Invoice Extension",
    "author": "Rauff Imasdeen",
    "email": "rauffmimas@gmailcom",
    "mobile": "0+971 5828 78 939",
    "version": "17.0",
    "license": "OPL-1",
    "depends": [
        'account',
        'fleet',
        'purchase',
        'base', 'sale_management','stock','purchase','fleet', 'tk_vehicle_management','uom','sale'
    ],
    "category": "Sales",

    "data": [

        # Reports
        'reports/invoice_report.xml',
        'reports/invoice_template.xml',
        'reports/report_service_note_document.xml',
        'reports/invoice_insurance_template.xml',


        'views/account_move_views.xml',
        'views/res_company_views.xml',
    ],
    "installable": True,
    "application": True,
}


