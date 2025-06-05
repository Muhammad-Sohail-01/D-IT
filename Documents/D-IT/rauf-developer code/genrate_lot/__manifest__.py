# -*- coding: utf-8 -*-

{
    "name": "Serial Lot Number auto generation",
    "author": "Rauff Imasdeen",
    "email": "rauffmimas@gmailcom",
    "mobile": "0+971 5828 78 939",
    "version": "17.0",
    "license": "OPL-1",
    "depends": [
        'stock',
        'sale_management',
        'purchase',
        'base',
    ],
    "category": "Sales",
    "summary": "Using this application you can can create serial lot number automatically while confirming purchase order, with cross-company serial number management.",
    "description": """
    Features:
    - Automatic serial number generation for external purchases
    - Cross-company serial number management
    - Serial number selection wizard for internal transfers
    - Supports tracking by unique serial numbers
    """,
    "data": [

        'security/ir.model.access.csv',
        'views/available_serial_view.xml',
        'views/serial_no.xml',
        'wizard/serial_number_wizard_view.xml',
        'views/stock_view_inherit.xml',
    ],
    "installable": True,
    "application": True,
}