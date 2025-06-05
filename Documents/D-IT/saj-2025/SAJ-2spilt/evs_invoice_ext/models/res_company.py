# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_vat_registered = fields.Boolean(string='VAT Registered', default=False)

    # Bank Details
    bank_name = fields.Char(string='Bank Name')
    account_name = fields.Char(string='Account Name')
    account_number = fields.Char(string='Account Number')
    iban = fields.Char(string='IBAN')
    swift_code = fields.Char(string='SWIFT Code')

    # Terms and Conditions
    invoice_terms = fields.Html(string='Invoice Terms & Conditions',
                                help="These terms & conditions will appear on customer invoices")

    print_template = fields.Binary(
        string='Invoice Template Design',
        help='Upload the complete print template.',
        attachment=True
    )



    def _get_report_templates(self):
        """Fetch all reports from ir.actions.report dynamically."""
        reports = self.env['ir.actions.report'].search([])
        return [(report.report_name, report.name) for report in reports]

    invoice_template_regular = fields.Selection(
        selection=_get_report_templates,
        string="Invoice Template (Regular)",
        help="Select the template format for regular invoices."
    )

    invoice_template_insurance = fields.Selection(
        selection=_get_report_templates,
        string="Invoice Template (Insurance)",
        help="Select the template format for insurance invoices."
    )

    sale_order_template = fields.Selection(
        selection=_get_report_templates,
        string="Sale Order Template",
        help="Select the template format for sale orders."
    )

