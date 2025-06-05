from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    po_order = fields.Boolean("Committe Order Approval", default=lambda self: self.env.company.po_double_validation == 'two_step')
    amount = fields.Float('Amont', readonly=False)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)


    @api.model
    def set_values(self):
        super().set_values()
        re = self.env['ir.config_parameter'].sudo()
        re.set_param('purchase_ext.amount', self.amount)

    @api.model
    def get_values(self):
        res = super().get_values()
        re = self.env['ir.config_parameter'].sudo()
        res['amount'] = float(re.get_param('purchase_ext.amount', default=0))
        return res
