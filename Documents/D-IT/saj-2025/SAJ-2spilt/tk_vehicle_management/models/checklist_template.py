from odoo import api, fields, models


class CheckListTemplate(models.Model):
    _name = 'checklist.template'
    _description = 'Check List Template'

    name = fields.Char(string="Name", required=True, translate=True)
    template_line_ids = fields.One2many('checklist.template.line', 'template_id')


class CheckTemplateLine(models.Model):
    _name = 'checklist.template.line'
    _description = "Checklist Template Lines"

    sequence = fields.Integer()
    name = fields.Char(string="Title", required=True)
    display_type = fields.Selection(selection=[('line_section', "Section"), ('line_note', "Note")], default=False)
    template_id = fields.Many2one('checklist.template')
