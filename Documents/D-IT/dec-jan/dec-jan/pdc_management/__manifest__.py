# -*- coding: utf-8 -*-

{
    "name": "Post Dated Cheque",

    "summary": "PDC Management,",
    "description": """ PDC Management, Report, in Odoo.""",
    "version": "17.0.1.0.1",
    "depends": [
        "account"
    ],


    'author': "Rauff M Imasdeen",
    'email': "rauffmimas@gmail.com",
    'mobile': "+971 582878939",

    "data": [
        "data/ir_sequence.xml",
        "data/account_data.xml",
        "data/ir_cron_cust.xml",
        # "data/ir_cron_ven.xml",
        "data/mail_templates.xml",
        "security/ir.model.access.csv",
        "security/pdc_security.xml",
        "wizard/pdc_payment_wizard_views.xml",
        "wizard/pdc_multi_action_views.xml",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "report/pdc_wizard_template.xml",
    ],
    "license": "OPL-1",
    "application": True,
    "auto_install": False,
    "installable": True,

    "post_init_hook": "post_init_hook"
}
