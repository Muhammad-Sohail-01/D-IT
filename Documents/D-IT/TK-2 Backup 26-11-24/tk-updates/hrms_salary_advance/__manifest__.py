# -*- coding: utf-8 -*-

{
    'name': 'HRMS Advance Salary',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Advance Salary Request',
    'description': "Advance Salary Request "
                   "company's staff.",
    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmailcom",
    'depends': [
        'hr',
        'hr_payroll',
        'hr_contract',
        'account_accountant',
        'hrms_loan',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/salary_structure.xml',
        'data/ir_sequence_data.xml',
        'views/salary_advance_views.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
}

