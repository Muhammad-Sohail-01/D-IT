
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime

class HrPaySlipExt(models.Model):
    _name = 'hr.payslip.affiliation.line'
    _description = 'Hr Pay Slip Input Type'


    name = fields.Many2one(comodel_name='res.company', string="Company")
    no_of_days = fields.Integer(string="No of Days")
    wage_percentage = fields.Float(string="Percentage(%)")
    base_currency_id = fields.Many2one('res.currency')
    wage_amount = fields.Monetary(currency_field='base_currency_id')
    affiliation_id = fields.Many2one('hr.payslip', string="Affiliation Id")

    @api.constrains('no_of_days')
    def _check_no_of_days(self):
        for record in self:
            # Get the current month and year
            # now = datetime.now()
            # month_days = calendar.monthrange(now.year, now.month)[1]  # Get total days in the current month
            month_days = rec.date_to - rec.date_from +1  # Get total days in the current month
            if record.no_of_days > month_days:
                raise ValidationError(_('No of Days cannot exceed %d days in the current month.') % month_days)
            if record.wage_percentage > 100:
                raise ValidationError(_('Percentage Cannot Exceed 100%.'))

    @api.model
    def create(self, vals):
        record = super(HrPaySlipExt, self).create(vals)
        record._check_no_of_days()  # Ensure validation after creation
        return record

    def write(self, vals):
        result = super(HrPaySlipExt, self).write(vals)
        self._check_no_of_days()  # Ensure validation after update
        return result

