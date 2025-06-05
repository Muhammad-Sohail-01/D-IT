from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrLoanTypeRequirement (models.Model):
    _name = 'hr.loan.type.requirement'
    _description = 'Loan Type Required Documents'
    _order = 'sequence, id'

    name = fields.Char (
        string='Document Name',
        required=True)

    loan_type_id = fields.Many2one (
        'hr.loan.type',
        string='Loan Type',
        required=True,
        ondelete='cascade')

    required = fields.Boolean (
        string='Mandatory',
        default=True,
        help="If checked, this document is mandatory for loan approval")

    sequence = fields.Integer (
        default=10,
        help="Determine the display order")

    description = fields.Text (
        string='Description',
        help="Additional information about the required document")

    document_format = fields.Many2many (
        'hr.loan.document.format',
        string='Allowed Formats',
        help="Allowed file formats for this document")

    max_file_size = fields.Float (
        string='Max File Size (MB)',
        default=10.0,
        help="Maximum allowed file size in megabytes")

    _sql_constraints = [
        ('unique_requirement_per_type',
         'UNIQUE(name, loan_type_id)',
         'Document requirement must be unique per loan type'),
        ('positive_file_size',
         'CHECK(max_file_size > 0)',
         'Maximum file size must be greater than zero')
    ]

    @api.constrains ('max_file_size')
    def _check_max_file_size(self):
        for record in self:
            if record.max_file_size > 100:  # 100 MB limit
                raise ValidationError (_ ('Maximum file size cannot exceed 100 MB'))


class HrLoanDocumentFormat (models.Model):
    _name = 'hr.loan.document.format'
    _description = 'Loan Document Format'
    _order = 'name'

    name = fields.Char (
        string='Format Name',
        required=True)

    extension = fields.Char (
        string='File Extension',
        required=True)

    mimetype = fields.Char (
        string='MIME Type',
        help="The MIME type for this format")

    active = fields.Boolean (
        default=True)

    _sql_constraints = [
        ('unique_extension',
         'UNIQUE(extension)',
         'File extension must be unique')
    ]

    def name_get(self):
        result = []
        for record in self:
            result.append ((record.id, f"{record.name} ({record.extension})"))
        return result