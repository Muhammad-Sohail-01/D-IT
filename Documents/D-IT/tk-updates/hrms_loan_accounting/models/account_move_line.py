# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLine(models.Model):
    """ Inheriting account move line for adding field. """
    _inherit = "account.move.line"

    loan_id = fields.Many2one(comodel_name='hr.loan', string='Loan Id',
                              help="Select loan details for employees")
