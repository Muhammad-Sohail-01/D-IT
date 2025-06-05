{
    'name': 'HR Loan and Advance Management',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee loans and advances',
    'description': """
        HR Loan and Advance Management for Odoo 17 Enterprise
        - Loan Management
        - Advance Management
        - Approval Workflows
        - Portal Access
    """,
    'author': 'Rauff M Imasdeen',
    'email': 'rauffmimas@gmail,com',
    'depends': [
        'hr',
        'hr_payroll',
        'account',
        'portal',
        'mail',
    ],
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/hr_loan_views.xml',
        'views/hr_loan_type_requirement_views.xml',
        'views/hr_loan_type_views.xml',
        # 'views/hr_advance_views.xml',
        'views/portal_templates.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}