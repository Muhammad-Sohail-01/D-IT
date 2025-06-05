# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class ResEmployee(models.Model):
	_inherit = 'hr.employee'

	job_accepted_date = fields.Date(string="Job Accepted Date")
	per_month_cost = fields.Float(string="Cost per Month")
#


# class EmpMulticom(models.Model):
# 	_inherit = 'hr.payslip'
#
# 	emp_multicom_id = fields.Many2one('emp.multicom',string="Employee multicom")
# 	company_id = fields.Many2one('res.company',string="Company")
# class Department(models.Model):
# 	_inherit = "hr.department"

#
#
#
# 	num_days = fields.Char(string="Number of Days",store=True)
# 	multicom_percentage = fields.Float(string="Percentage(%)")
# 	multicom_amount = fields.Float(string="Wage Amount",compute="_compute_multicom_amount",store=True)
# 	hr_payslip_id = fields.Many2one('hr.payslip',string="Payslip No")
#
#
# 	# @api.depends('hr_payslip_id', 'per_day_cost', 'wage_percentage')
# 	# def _compute_multicom_amount(self):
# 	# 	for multicom in self:
# 	# 		wage_amount = 0
# 	# 		if multicom.wage_percentage > 0:
# 	# 			wage_amount = (per_day_cost * multicom.wage_percentage) / 100
# 	# 		multicom.wage_amount = wage_amount
# #
# # 	@api.onchange('emp_multicom_id')
# # 	def _onchange_emp_multicom(self):
# # 		for emp in self:
# # 			if emp.emp_multicom_id and emp.emp_multicom_id.company_id:
# # 				emp.company_id = emp.emp_multicom_id.company_id.id
# #
#
#
# 	@api.depends('per_month_cost', 'num_days')
# 	def _compute_multicom_amount(self):
# 		for multicom in self:
# 			if multicom.num_days > 0:
# 				daily_cost = multicom.per_month_cost / calendar.monthrange(multicom.year, multicom.month)[1]
# 				multicom.multicom_amount = multicom.num_days * daily_cost
# 			else:
# 				multicom.multicom_amount = (multicom.per_month_cost * multicom.multicom_percentage) / 100
#
# 				@api.multi
# 				def action_generate_multicom(self):
# 					for multicom in self:
# 						if multicom.emp_multicom_id and multicom.emp_multicom_id.company_id:
# 							intercompany_journal = self.env['account.journal'].search(
# 								[('name', '=', 'Intercompany Journal'),
# 								 ('company_id', '=', multicom.emp_multicom_id.company_id.id)], limit=1)
# 							if intercompany_journal:
# 								move = self.env['account.move'].create({
# 									'journal_id': intercompany_journal.id,
# 									'date': multicom.date_to,
# 									'ref': multicom.name,
# 									'company_id': multicom.emp_multicom_id.company_id.id,
# 									'line_ids': [(0, 0, {
# 										'account_id': multicom.account_id.id,
# 										'partner_id': multicom.emp_multicom_id.company_id.partner_id.id,
# 										'debit': multicom.multicom_amount,
# 										'credit': 0,
# 										'name': 'Multicom',
# 										'date_maturity': multicom.date_to,
# 										'ref': multicom.name,
# 										'company_id': multicom.emp_multicom_id.company_id.id,
# 										'currency_id': multicom.emp_multicom_id.company_id.currency_id.id,
# 									})]
# 								})
# 								move.post()
#
#
