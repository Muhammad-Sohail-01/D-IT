# -*- coding: utf-8 -*-
from odoo import fields, models


class HrLoanLine(models.Model):
    """
        Class for creating installment details
    """
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True,
                       help="Date of the payment")
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee",
                                  help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one(comodel_name='hr.loan', string="Loan Ref.",
                              help="Loan")
    payslip_id = fields.Many2one(comodel_name='hr.payslip',
                                 string="Payslip Ref.",
                                 help="Payslip")
