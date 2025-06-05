# -*- coding: utf-8 -*-

{
    'name': 'Print Journal Entries Report in Odoo',
    'version': '17.0.0.1',
    'category': 'Account',
    'summary': 'Print - Journal Entries.',
    'description': """Journal Print Out 
""",
   
    'author': 'Rauff M Imasdeen',
    'email': 'rauffmimas@gmail.com',
    'mobile': '+971582878939',
    'depends': ['base','account'],

    'data': [
            'report/report_journal_entries.xml',
            'report/report_journal_entries_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
