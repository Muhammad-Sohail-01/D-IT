# -*- coding: utf-8 -*-

{
    'name': 'HRMS Loan',
    'version': '17.0.1.0.3',
    'category': 'Human Resources',
    'summary': 'Loan Request',
    'description': "Loan Request "
                   "company's staff.",
    'author': "Rauff M Imasdeen",
    'Email': "rauffmimas@gmailcom",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account',
    ],
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/hr_payroll_structure_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_payslip_input_type_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_loan_views.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_salary_rule_views.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
