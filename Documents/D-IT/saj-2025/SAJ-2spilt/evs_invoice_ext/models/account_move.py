# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class AccountMove (models.Model):
    _inherit = 'account.move'

    job_card_idd = fields.Many2one (
        'vehicle.inspection',
        string="Job Card",
        domain="[('customer_id', '=', partner_id)]"
    )

    register_vehicle_id = fields.Many2one (
        'register.vehicle',
        string="Vehicle",
        domain="[('customer_id', '=', partner_id)]"
    )

    # Vehicle Related Fields - copied from sale.order
    brand_id = fields.Many2one ('fleet.vehicle.model.brand', related='register_vehicle_id.brand_id', string="Brand", store=True)
    vehicle_model_id = fields.Many2one (related="register_vehicle_id.vehicle_model_id", string="Model", store=True)
    vin_no = fields.Char (related="register_vehicle_id.vin_no", string="VIN NO.", store=True)
    registration_no = fields.Char (related="register_vehicle_id.registration_no", string="Registration No", store=True)
    year = fields.Char (related="register_vehicle_id.year", string="Year", store=True)
    color = fields.Selection (related="register_vehicle_id.color", string="Color", store=True)


    @api.onchange ('partner_id')
    def _onchange_partner_id(self):
        super ()._onchange_partner_id ()
        # Clear the fields when partner changes
        self.job_card_idd = False
        self.register_vehicle_id = False

    @api.onchange ('job_card_idd')
    def _onchange_job_card_idd(self):
        if self.job_card_idd:
            self.register_vehicle_id = self.job_card_idd.register_vehicle_id
    # register_vehicle_id = fields.Many2one ('register.vehicle',
    #                                        domain="[('customer_id','=',partner_id)]", store=True)
    # brand_id = fields.Many2one ('fleet.vehicle.model.brand',
    #                             related='register_vehicle_id.brand_id', store=True)
    # vehicle_model_id = fields.Many2one (related="register_vehicle_id.vehicle_model_id",
    #                                     string="Model", store=True)
    # vin_no = fields.Char (related="register_vehicle_id.vin_no",
    #                       string="VIN NO.", store=True)
    # registration_no = fields.Char (related="register_vehicle_id.registration_no",
    #                                string="Registration No", store=True)
    # year = fields.Char (related="register_vehicle_id.year",
    #                     string="Year", store=True)
    # color = fields.Selection (related="register_vehicle_id.color",
    #                           string="Color", store=True)
    service_advisor_id = fields.Many2one ('res.users', string="Service Advisor")

    # Job Card Related Fields
    job_card_count = fields.Integer (compute="_compute_count")
    job_card_idd = fields.Many2one ('vehicle.inspection')

    def _compute_count(self):
        for record in self:
            record.job_card_count = self.env['vehicle.inspection'].sudo().search_count(
                [('sale_order_id', '=', record.id)]
            )

    def action_redirect_to_job_card(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card',
            'res_model': 'vehicle.inspection',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'tree,form',
            'target': 'current'
        }


class AccountMoveLine (models.Model):
    _inherit = 'account.move.line'

    # Part Related Fields
    part_nubmer_id = fields.Many2one ('auto.mobile.partno.line', string="Part Number", store=True)
    part_internal_no = fields.Char (string="Internal No")
    brand_id = fields.Many2one ('fleet.vehicle.model.brand', string="Brand",
                                domain=[('part_no_id', '=', 'product_id')])
    model_id = fields.Many2one ('fleet.vehicle.model', string="Model")
    warranty_applicable = fields.Boolean (string="Warranty Appl")
    estimate_time = fields.Float (string="Estimate Time")
    allowed_hour_change = fields.Boolean (string="Hours allowed change",
                                          related="product_id.allowed_hour_change")

    available_brand_ids = fields.Many2many (
        'fleet.vehicle.model.brand',
        'account_move_line_brand_rel',
        compute='_compute_available_brand_ids',
        string="Available Brands"
    )

    available_model_ids = fields.Many2many (
        'fleet.vehicle.model',
        'account_move_line_model_rel',
        compute='_compute_available_model_ids',
        string="Available Models"
    )

    warranty_expiry_date = fields.Date (string="Warranty Expiry Date",
                                        compute="_compute_warranty_expiry_date",
                                        readonly=False, store=True)

    @api.depends ('warranty_applicable')
    def _compute_warranty_expiry_date(self):
        for line in self:
            expiry_date = False
            if line.product_id and hasattr (line.product_id, 'is_warranty'):
                duration = line.product_id.duration
                period = line.product_id.period
                if line.product_id.is_warranty:
                    if period == '12':  # Years
                        expiry_date = fields.Date.context_today (line) + relativedelta (years=duration)
                    elif period == '1':  # Months
                        expiry_date = fields.Date.context_today (line) + relativedelta (months=duration)
            line.warranty_expiry_date = expiry_date

    @api.depends ('product_id')
    def _compute_available_brand_ids(self):
        for line in self:
            if line.product_id:
                # Get all related brands from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search ([
                    ('partno_id', '=', line.product_id.product_tmpl_id.id)
                ])
                brand_ids = partno_lines.mapped ('brand_ids').ids
                line.available_brand_ids = [(6, 0, brand_ids)]
            else:
                line.available_brand_ids = [(6, 0, [])]

    @api.depends ('product_id')
    def _compute_available_model_ids(self):
        for line in self:
            if line.product_id:
                # Get all related models from the partno lines
                partno_lines = self.env['auto.mobile.partno.line'].search ([
                    ('partno_id', '=', line.product_id.product_tmpl_id.id)
                ])
                model_ids = partno_lines.mapped ('model_ids').ids
                line.available_model_ids = [(6, 0, model_ids)]
            else:
                line.available_model_ids = [(6, 0, [])]

    @api.onchange ('part_nubmer_id')
    def _onchange_part_nubmer_id(self):
        if not self.part_nubmer_id:
            return

        if self.part_nubmer_id.partno_id:
            # Set the product directly using product_id
            product_tmpl = self.part_nubmer_id.partno_id
            if product_tmpl.product_variant_ids:
                self.product_id = product_tmpl.product_variant_ids[0]
                self.name = self.product_id.name
                self.product_uom_id = self.product_id.uom_id
                self.part_internal_no = self.part_nubmer_id.part_internal_no

        # Check if the selected part number has a sale price
        if self.part_nubmer_id.sale_price:
            self.price_unit = self.part_nubmer_id.sale_price
        else:
            # Fallback to the list price if there's no sale price
            self.price_unit = self.product_id.list_price

            # Display warning if there's a note
        if self.part_nubmer_id.note:
            return {
                'warning': {
                    'title'  : _ ("Warning for Part %s", self.part_nubmer_id.partno),
                    'message': self.part_nubmer_id.note,
                }
            }

    @api.onchange ('warranty_applicable')
    def _onchange_warranty_applicable(self):
        if self.warranty_applicable:
            self.price_unit = 0.0