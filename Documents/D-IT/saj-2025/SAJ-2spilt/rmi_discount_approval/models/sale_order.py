from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_required = fields.Boolean(
        string="Approval Required",
        default=False,
        tracking=True
    )

    def action_confirm(self):
        for order in self:
            if order.approval_required:
                raise ValidationError("Approval is required before confirming this sale order.")
        return super(SaleOrder, self).action_confirm()

    def schedule_approval_activity(self):
        for order in self:
            approvers = self.env['res.users'].search([('approve_discount', '=', True)])
            if not approvers:
                raise ValidationError("No approvers available for this sale order.")
        
            if not order.id:
                self.env.cr.flush()  # Flush changes to the database to ensure order exists
        
            for approver in approvers:
                activity = self.env['mail.activity'].create({
                'res_id': 67,
                'res_model_id': self.env['ir.model']._get_id('sale.order'),
                'user_id': approver.id,
                'summary': 'Follow up with the customer',
                'date_deadline': fields.Date.today(),
            })




    
    def action_approve_discount(self):
        """
        Approve the discount for the sale order.
        """
        for order in self:
            if order.approval_required:
                # Mark approval as granted and set the approval status
                order.approval_required = False
                order.state = 'sale'  # Change state to 'sale' or another status based on your flow
                order.message_post(
                    subject="Discount Approved",
                    body=f"Discount for sale order {order.name} has been approved."
                )
            else:
                raise UserError("No approval required for this sale order.")
