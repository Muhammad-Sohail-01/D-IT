from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError



class VehicleInspectionTaskInheritStage(models.Model):
    _inherit = 'product.category'


    deferred_revenue_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Deferred Revenue',
        help='Account used for deferred revenues',
        
    )
    deferred_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Deferred Expense',
        help='Account used for deferred expenses',
    )
    deferred_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Deferred Journal",
    )
    


    def price_fixed(self):
        pass
   


class AccountMove(models.Model):
    _inherit = 'account.move'

    from odoo import models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    from odoo import models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _generate_deferred_entries(self):
        """
        Override to modify specific deferred accounts after generating entries.
        """
        # Call the original method to generate deferred entries
        super(AccountMove, self)._generate_deferred_entries()

        # Determine the default deferred account
        is_deferred_expense = self.is_purchase_document()
        default_deferred_account = self.company_id.deferred_expense_account_id if is_deferred_expense else self.company_id.deferred_revenue_account_id

        # Apply custom logic to modify deferred accounts only for matching default deferred accounts
        for move in self.deferred_move_ids:
            for line in move.line_ids:
                # Ensure the line's account matches the default deferred account
                if line.account_id == default_deferred_account:
                    # Fetch the related original line from the `move_id`
                    original_line = line.move_id.line_ids.filtered(
                        lambda l: l.product_id and l.product_id.is_warranty
                    )
                    if original_line:
                        # Determine the custom deferred account from the product category
                        custom_account = (
                            original_line.product_id.categ_id.deferred_expense_account_id
                            if is_deferred_expense
                            else original_line.product_id.categ_id.deferred_revenue_account_id
                        )
                        if not custom_account:
                            raise UserError(
                                _("Deferred account is not set for the category of product '%s'.") % original_line.product_id.display_name
                            )

                        # Update the account on the deferred move line
                        line.account_id = custom_account


    
            




    


    
    

    



















        






    
