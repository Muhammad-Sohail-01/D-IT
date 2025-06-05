from odoo import api, fields, models


class VehicleResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    quot_expire_days = fields.Integer(string="Quotation Expire Days", default=7,
                                      config_parameter='tk_vehicle_management.quot_expire_days')
    quotation_term = fields.Char(string="Quotation Term Link",
                                 config_parameter='tk_vehicle_management.quot_term')
    general_service_id = fields.Many2one('product.product',
                                         domain="[('detailed_type','=','service')]",
                                         config_parameter='tk_vehicle_management.general_service_id',
                                         string="General Service")

    # Whatsapp : Appointment Template
    wa_template_appointment_reminder_week_id = fields.Many2one(comodel_name='whatsapp.template',
                                                               string="Appointment Reminder : 2 Week",
                                                               domain="[('model','=','calendar.event')]",
                                                               config_parameter="tk_vehicle_management.wa_template_appointment_reminder_week_id")
    wa_template_appointment_reminder_day_id = fields.Many2one(comodel_name='whatsapp.template',
                                                              string="Appointment Reminder : 1 Day",
                                                              domain="[('model','=','calendar.event')]",
                                                              config_parameter="tk_vehicle_management.wa_template_appointment_reminder_day_id")
    wa_template_appointment_miss_id = fields.Many2one(comodel_name='whatsapp.template',
                                                      string="Appointment : Miss Appointment",
                                                      domain="[('model','=','calendar.event')]",
                                                      config_parameter="tk_vehicle_management.wa_template_appointment_miss_id")

    # Whatsapp : Quotation Template
    wa_quot_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                          string="Quotation Whatsapp Template",
                                          domain="[('model','=','vehicle.inspection')]",
                                          config_parameter="tk_vehicle_management.wa_quot_template_id")
    wa_additional_quot_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                                     string="Additional Part Quotation Whatsapp Template",
                                                     domain="[('model','=','vehicle.inspection')]",
                                                     config_parameter="tk_vehicle_management.wa_additional_quot_template_id")

    # Whatsapp : Consent
    wa_consent_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                             string="Consent Whatsapp Template",
                                             domain="[('model','=','vehicle.inspection')]",
                                             config_parameter="tk_vehicle_management.wa_consent_template_id")
    consent_expire_days = fields.Integer(string="Consent Expire Days", default=1,
                                         config_parameter='tk_vehicle_management.consent_expire_days')

    # Whatsapp : Task QC Check
    wa_team_leader_qc_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                                    string="Team Leader QC Whatsapp Template (Task)",
                                                    domain="[('model','=','project.task')]",
                                                    config_parameter="tk_vehicle_management.wa_team_leader_qc_template_id")
    wa_qc_check_complete_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                                       string="Team Leader QC Completed Whatsapp Template",
                                                       domain="[('model','=','vehicle.inspection')]",
                                                       config_parameter="tk_vehicle_management.wa_qc_check_complete_template_id")

    # Whatsapp : Booking Create Notification
    wa_check_in_service_advisor_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                                              string="Service Advisor : Check-in Create Notification Template",
                                                              domain="[('model','=','vehicle.booking')]",
                                                              config_parameter="tk_vehicle_management.wa_check_in_service_advisor_template_id")
    wa_check_in_customer_template_id = fields.Many2one(comodel_name='whatsapp.template',
                                                       string="Customer : Check-in Create Notification Template",
                                                       domain="[('model','=','vehicle.booking')]",
                                                       config_parameter="tk_vehicle_management.wa_check_in_customer_template_id")

    # Shop Supply Product
    shop_supply_product_id = fields.Many2one(comodel_name='product.product',
                                             string="Shop Supplies and Environmental Default Product",
                                             config_parameter="tk_vehicle_management.shop_supply_product_id")

    # Accounting Advance Payment
    advance_payment_journal_id = fields.Many2one('account.journal',
                                                 config_parameter="tk_vehicle_management.advance_payment_journal_id",
                                                 domain="[('id', 'in', available_journal_ids)]")
    available_journal_ids = fields.Many2many('account.journal',
                                             compute="_compute_available_journal_ids")

    advance_payment_status = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')],
                                              default='posted',
                                              config_parameter="tk_vehicle_management.advance_payment_status")
    invoice_status = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')],
                                      default='posted',
                                      config_parameter="tk_vehicle_management.invoice_status")

    # DEPRECATED
    vehicle_parts_warehouse_id = fields.Many2one(comodel_name='stock.warehouse',
                                                 string="Parts Warehouse",
                                                 config_parameter='tk_vehicle_management.vehicle_parts_warehouse_id')

    #warranty applicable journal
    service_note_journal_id = fields.Many2one (
        'account.journal',
        domain="[('company_id', '=', company_id)]"
    )

    @api.depends('advance_payment_journal_id')
    def _compute_available_journal_ids(self):
        """
        Get all journals having at least one payment method for inbound/outbound depending on the payment_type.
        """
        journals = self.env['account.journal'].search([
            '|',
            ('company_id', 'parent_of', self.env.company.id),
            ('company_id', 'child_of', self.env.company.id),
            ('type', 'in', ('bank', 'cash')),
        ])
        for pay in self:
            pay.available_journal_ids = journals.filtered('inbound_payment_method_line_ids')


    def set_values(self):
        super (VehicleResConfig, self).set_values ()
        # Save service note journal for the current company
        self.env['ir.config_parameter'].sudo ().set_param (
            f'tk_vehicle_management.service_note_journal_id_{self.env.company.id}',
            self.service_note_journal_id.id if self.service_note_journal_id else False
        )

    @api.model
    def get_values(self):
        res = super (VehicleResConfig, self).get_values ()
        # Fetch service note journal for the current company
        service_note_journal_id = self.env['ir.config_parameter'].sudo ().get_param (
            f'tk_vehicle_management.service_note_journal_id_{self.env.company.id}'
        )
        res.update (
            service_note_journal_id=int (service_note_journal_id) if service_note_journal_id else False
        )
        return res
