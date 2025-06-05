# -*- coding: utf-8 -*-

{
    'name': 'HRMS Loan Accounting',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Loan Accounting',
    'description': """Manage Loan Request and Accounting.""",
    'author': "Rauff Imasdeen",
    'Email': "rauffmimas@gmail.com",
    'depends': [
        'hr_payroll',
        'hr',
        'account',
        'account_accountant',
        'hrms_loan'
    ],
    'data': [
        'views/hr_loan_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
