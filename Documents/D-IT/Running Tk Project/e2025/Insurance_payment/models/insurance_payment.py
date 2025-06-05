from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InsurancePayment(models.Model):
    _name = 'insurance.payment'  # This defines the model
    _description = 'Insurance Payment'

    insurance_invoice = fields.Boolean(default=False, string="Insurance Invoice")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    insurance_journal_date = fields.Date(related="insurance_journal_entry_id.date", string="Journal Date")
    insurance_journal_name = fields.Char(related="insurance_journal_entry_id.name", string="Journal Voucher No")
    insurance_journal_entry_id = fields.Many2one('account.move', string="Insurance Journal Entry")

    insurance_invoice = fields.Boolean(default=False, string="Insurance Invoice")
    insurance_company = fields.Many2one(
        comodel_name='res.partner',
        string="Insurance Company",
        domain="[('category_id.name', '=', 'Insurance')]"
    )
    amount_nature = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ], default='fixed', string="Amount Nature")
    receivable_amount = fields.Float(
        string="Receivable Amount",
        compute="_compute_receivable_amount",
        store=True,
    )
    receivable_insurance_fix = fields.Monetary(
        string="Receivable Insurance (Fixed)",
        compute="_compute_receivable_insurance_fix",
        readonly=False,
        store=True
    )
    insurance_amount_percentage = fields.Float(
        string="Insurance Amount %",
        compute="_compute_insurance_amount_percentage",
        readonly=False,
        store=True
    )
    policy_no = fields.Char('Policy No')
    insurance_journal = fields.Many2one('account.journal', string="Insurance Journal")

    # vin_no = fields.Char(related="job_card_id.vin_no", string="VIN NO.")
    # registration_no = fields.Char(related="job_card_id.registration_no", string="Registration No")
    # job_card_count = fields.Integer(compute="_compute_count")
    # job_card_idd = fields.Many2one('vehicle.inspection')

    @api.depends('amount_nature', 'receivable_insurance_fix', 'insurance_amount_percentage', 'order_line')
    def _compute_receivable_amount(self):
        for rec in self:
            if rec.amount_nature == 'fixed':
                rec.receivable_amount = rec.receivable_insurance_fix
            elif rec.amount_nature == 'percentage':
                total_order_amount = sum(rec.order_line.mapped('price_subtotal'))
                rec.receivable_amount = total_order_amount * (rec.insurance_amount_percentage / 100)
            else:
                rec.receivable_amount = 0

    @api.depends('amount_nature', 'receivable_amount')
    def _compute_receivable_insurance_fix(self):
        for rec in self:
            if rec.amount_nature == 'fixed':
                rec.receivable_insurance_fix = rec.receivable_amount
            else:
                rec.receivable_insurance_fix = 0

    @api.depends('amount_nature', 'receivable_amount', 'order_line')
    def _compute_insurance_amount_percentage(self):
        for rec in self:
            if rec.amount_nature == 'percentage' and rec.order_line:
                total_order_amount = sum(rec.order_line.mapped('price_subtotal'))
                if total_order_amount > 0:
                    rec.insurance_amount_percentage = (rec.receivable_amount / total_order_amount) * 100
                else:
                    rec.insurance_amount_percentage = 0
            else:
                rec.insurance_amount_percentage = 0



    def create_insurance_journal_entry(self):
        for order in self:
            if not order.insurance_company:
                raise UserError(_("Please select an Insurance Company."))

            journal = self.env['account.journal'].search([
                ('name', '=', 'Insurance Journal'),
                ('company_id', '=', order.company_id.id)
            ], limit=1)
            if not journal:
                raise UserError(_("No valid journal found for the insurance journal."))

            if not order.receivable_amount:
                raise UserError(_("Receivable amount is zero. Please check your calculations."))

            currency = order.currency_id
            move_lines = []

            # # Debit: Customer receivable account
            # move_lines.append((0, 0, {
            #     'account_id': order.partner_id.property_account_receivable_id.id,
            #     'partner_id': order.partner_id.id,
            #     'name': f"{order.name} Paid by insurance",
            #     # 'name': f"{order.name} - {order.job_card_id.name if order.job_card_id else ''} {order.vin_no}- Paid by insurance",
            #     'debit': order.receivable_amount,
            #     'credit': 0.0,
            #     'currency_id': currency.id,
            #     'amount_currency': order.receivable_amount
            # }))
            #
            # # Credit: Insurance company receivable account
            # move_lines.append((0, 0, {
            #     'account_id': order.insurance_company.property_account_receivable_id.id,
            #     'partner_id': order.insurance_company.id,
            #     'name': f"{order.name} - Allocating to Insurance",
            #     # 'name': f"{order.name} - {order.vin_no} - Allocating to Insurance",
            #     'debit': 0.0,
            #     'credit': order.receivable_amount,
            #     'currency_id': currency.id,
            #     'amount_currency': -order.receivable_amount
            # }))

            # Debit: Insurance company receivable account
            move_lines.append((0, 0, {
                'account_id': order.insurance_company.property_account_receivable_id.id,
                'partner_id': order.insurance_company.id,
                'name': f"{order.name} Paid by insurance",
                # 'name': f"{order.name} - {order.vin_no} - Allocating to Insurance",
                'debit': order.receivable_amount,
                'credit': 0.0,
                'currency_id': currency.id,
                'amount_currency': order.receivable_amount
            }))

            # Credit: Customer receivable account
            move_lines.append((0, 0, {
                'account_id': order.partner_id.property_account_receivable_id.id,
                'partner_id': order.partner_id.id,
                'name': f"{order.name} - Allocating to Insurance",
                # 'name': f"{order.name} - {order.job_card_id.name if order.job_card_id else ''} {order.vin_no}- Paid by insurance",
                'debit': 0.0,
                'credit': order.receivable_amount,
                'currency_id': currency.id,
                'amount_currency': -order.receivable_amount
            }))

            move_vals = {
                'journal_id': journal.id,
                'ref': f"{order.name} ",
                # 'ref': f"{order.name} - {order.vin_no}",
                'date': order.date_order,
                'line_ids': move_lines,
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            order.insurance_journal_entry_id = move.id

            # Add a message to the chatter
            order.message_post(body=_("Insurance journal entry created: %s") % move.name)

        # @api.depends(insurance_journal_entry_id)
        # def reverse_insurance_journal_entry(self):
        #         for order in self:
        #             if not order.insurance_journal_entry_id:
        #                 raise UserError(_("No insurance journal entry found to reverse."))
        #
        #             # Reverse the journal entry
        #             reversal = order.insurance_journal_entry_id._reverse_moves(
        #                 default_values_list=[{'date': fields.Date.today()}],
        #             )
        #             reversal.action_post()
        #
        #             # Update the state and clear the journal entry ID
        #             order.insurance_journal_entry_id = False
        #
        #
        #
        #             # Add a message to the chatter
        #             order.message_post(body=_("Insurance journal entry reversed: %s") % reversal.name)