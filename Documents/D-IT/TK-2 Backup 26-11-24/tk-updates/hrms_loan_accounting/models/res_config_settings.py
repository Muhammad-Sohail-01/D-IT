# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inheriting res config settings for adding fields. """
    _inherit = 'res.config.settings'

    loan_approve = fields.Boolean(default=False,
                                  config_parameter="account.loan_approve",
                                  string="Approval from Accounting Department",
                                  help="Loan Approval from account manager")
