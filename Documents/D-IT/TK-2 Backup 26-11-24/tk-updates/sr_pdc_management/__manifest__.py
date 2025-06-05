# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': "Post Dated Cheque Management",
    'version': "17.0.0.0",
    'summary': "This modules helps you to manage Post dated cheques.",
    'category': 'Accounting & Finance',
    'description': """
    This modules helps you to manage Post dated cheques.
    Post dated cheques
    manage post dated cheques
    apply post dated cheques
    cheques management
    manage cheques
    pdc management
    register post dated cheques
    register PDC
    PDC payment
    cheques manage
    Manage Cheques
    Manage PDC
    Cheque life cycle management
    account cheque management
    bank cheque management
    Post dated cheques in odoo
    post dated cheque management in odoo
    post dated cheque module
    post dated cheque application
    Post dated checks
    Security checks
    Manage accounts using post dated checks
    Security cheque
    Manage accounts using post dated cheque
    """,
    'author': "Sitaram",
    'website':"https://www.sitaramsolutions.in",
    'depends': ['base', 'sale_management','account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/pdc_payment_view.xml',
        'views/inherited_account_invoice.xml',
        'views/inherited_invoice_setting.xml',
        'reports/report_pdc.xml',
        'reports/pdc_report_template.xml'
    ],
    'demo': [],
    "external_dependencies": {},
    "license": "OPL-1",
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://www.youtube.com/watch?v=P3GTFjzGtpY&t=102s',
    'images': ['static/description/banner.png'],
    "price": 50,
    "currency": 'EUR',
    
}
