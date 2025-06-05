{
    'name': 'HR Intercompany Payroll',
    'version': '17.0.0.1.3',
    'summary': 'Model for managing intercompany payroll allocations',
    'description': 'Module to allocate payroll across multiple companies.',
    'category': 'Human Resources',
    'author': 'Rauff Imasdeen',
    'email': 'rauffmimas@gmail.com',
    'mobile': '+971 5828 78 939',
    'license': 'LGPL-3',

    'depends': ['hr', 'hr_payroll', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_salary_distribution_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
