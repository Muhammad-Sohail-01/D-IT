# -*- coding: utf-8 -*-
{
    "name": "PDC Management",
    "version": "17.0.3.0.1",
    "summary": "Post-Dated Cheque Management System",
    "description": """
        Post-Dated Cheque (PDC) Management System for Odoo 17
        ===================================================

        Features:
        ---------
            * PDC Payment handling in Account Payments
            * Dedicated PDC Journals Configuration
            * PDC Receivable and Payable Account Management
            * Automatic Journal Entry Creation for PDCs
            * PDC Date and Number Tracking
    """,
    'category': 'Accounting/Payment',
    'author': 'Rauff M Imasdeen',
    'company': 'AccFeed Online',
    'maintainer': 'AccFeed Online',
    'website': 'https://www.accfeedonline.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_payment_views.xml',
        'views/account_journal_views.xml',
        'views/account_payment_register_view.xml',
    ],

    'images': ['static/description/icon.png'],
    'installable' : True,
    'application' : True,
    'auto_install': False,

    'support': 'support@accfeedonline.com',
    'contributors': ['Rauff M Imasdeen <rauff@accfeedonline.com>'],
}
