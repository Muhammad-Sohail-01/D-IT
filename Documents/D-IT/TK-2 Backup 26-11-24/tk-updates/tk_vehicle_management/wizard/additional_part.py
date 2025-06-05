from odoo import fields, api, models


class InspectionAdditionalPart(models.TransientModel):
    """Insert Additional Part"""
    _name = 'inspection.additional.part'
    _description = 'Additional Part'

    product_id = fields.Many2one('product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                  string='Currency')
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    price = fields.Monetary(string="Unit Price")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Monetary(string="Tax Amount", compute="_compute_total_amount")
    untaxed_amount = fields.Monetary(string="Untaxed Amount", compute="_compute_total_amount")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount")
    inspection_id = fields.Many2one(comodel_name='vehicle.inspection')
    service_ids = fields.Many2many('vehicle.required.services', string="Services",
                                   compute="compute_services")
    service_id = fields.Many2one('vehicle.required.services', string="Service",
                                 domain="[('id','in',service_ids)]")
    required_time = fields.Float(string="Required Time")

    is_link_with_task = fields.Boolean(string="Link With Task")

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(InspectionAdditionalPart, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['inspection_id'] = active_id
        return res

    @api.onchange('product_id')
    def onchange_product_info(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.price = rec.product_id.lst_price

    @api.depends('qty', 'product_id', 'price', 'tax_ids', 'tax_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0
            tax_amount = 0.0
            if rec.product_id:
                total_tax_percentage = sum(
                    data.amount if data.amount_type != 'group' else sum(
                        data.children_tax_ids.mapped('amount'))
                    for data in rec.tax_ids
                )
                total = rec.qty * rec.price
                tax_amount = total_tax_percentage * total / 100
            rec.total_amount = total + tax_amount
            rec.tax_amount = tax_amount
            rec.untaxed_amount = total

    @api.depends('inspection_id', 'inspection_id.inspection_required_service_ids')
    def compute_services(self):
        for rec in self:
            rec.service_ids = rec.inspection_id.inspection_required_service_ids.filtered(
                lambda line: not line.display_type and line.service_selected).mapped('id')

    def action_add_additional_part(self):
        """Process Additional Part"""
        additional_part_id = False
        if self.is_link_with_task:
            additional_part_id = self.env['task.additional.parts'].create({
                'task_id': self.service_id.task_id.id,
                'product_id': self.product_id.id,
                'name': self.name,
                'qty': self.qty,
                'required_time': self.required_time,
                'service_id': self.service_id.id,
                'status': 'requested'
            })
        self.env['vehicle.required.parts'].create({
            'product_id': self.product_id.id,
            'name': self.name,
            'qty': self.qty,
            'price': self.price,
            'vehicle_health_report_id': self.inspection_id.vehicle_health_report_id.id,
            'inspection_id': self.inspection_id.id,
            'service_id': self.service_id.id,
            'is_additional_part': True,
            'required_time': self.required_time,
            'additional_part_id': additional_part_id.id if additional_part_id else False,
            'tax_ids': [(6, 0, self.tax_ids.ids)] if self.tax_ids else [],
        })
        self.inspection_id.update_quot_mail = True
