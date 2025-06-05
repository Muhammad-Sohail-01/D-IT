# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Multi Company Salary',
    'version': '17.1.2',
    'category': 'HR Employee',
    'sequence': '1',
    'summary': 'Multi Company Salary',
    'description': """
            Multicompany Salary divided by company
        """,
    'author': 'Rauff M Imasdeen',
    'Email': 'rauffmimas@gmailcom',
    'Mobile No': '+971 58 28 78 939',
    'depends': [
        'hr',
        'hr_contract',
        'hr_payroll',
        'hr_contract_salary',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_multicom_views.xml',
        'views/hr_payslip_ext.xml',
    ],
    'assets': {},
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
