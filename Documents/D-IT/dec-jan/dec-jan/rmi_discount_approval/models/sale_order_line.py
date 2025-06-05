from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_approved = fields.Boolean(string="Discount Approved", default=False)
    approver_id = fields.Many2one('res.users', string="Approved By")

    @api.model
    def create(self, vals):
        """
        Override the create method to add custom logic during record creation.
        """
        # Create the order line first
        record = super(SaleOrderLine, self).create(vals)
        # Check if a discount exists and needs to be validated
        if record.discount > 0:  # Apply your specific validation logic
            record._validate_discount()
        return record

    def write(self, vals):
        """
        Override the write method to add custom logic when records are updated.
        """
        res = super(SaleOrderLine, self).write(vals)
        if 'discount' in vals:
            # If the discount is changed, validate it
            for line in self:
                line._validate_discount()
        return res

    def _validate_discount(self):
        """
        The discount validation method.
        """
        for line in self:
            max_discount = line.product_id.desc_limit or line.product_id.categ_id.desc_limit
            user = line.order_id.user_id
            user_max_discount = user.max_discount

            

            if max_discount and line.discount > max_discount:
                if not user.allow_discount:
                    approvers = self.env['res.users'].search([('approve_discount', '=', True)])
                    if not approvers:
                        raise ValidationError("No approvers are available for this sale order.")
                    
                    # Trigger approval activity
                    order = line.order_id
                    order.approval_required = True
                    
                    for approver in approvers:
                        activity = self.env['mail.activity'].create({
                            'res_id': order.id,  # Corrected from self.id to order.id
                            'activity_type_id':4,
                            'res_model_id': self.env['ir.model']._get_id('sale.order'),
                            'user_id': approver.id,
                            'summary': 'Approve Discount',
                            'note': f"Discount Approval is required for the sale order <b>{order.name}</b>.",
                            'date_deadline': fields.Date.today(),
                        })

                
                else:
                    line.discount_approved = True
                    line.approver_id = user.id
            else:
                line.discount_approved = True

