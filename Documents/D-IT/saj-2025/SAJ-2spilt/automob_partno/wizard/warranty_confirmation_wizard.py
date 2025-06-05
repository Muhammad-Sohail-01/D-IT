from odoo import fields, api, models

class WarrantyConfirmationWizard(models.TransientModel):
    _name = 'warranty.confirmation.wizard'
    _description = 'Warranty Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

    def action_confirm(self):
        """This method runs when 'Yes' is clicked"""
        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)
        if sale_order:
            sale_order.action_confirm()

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
