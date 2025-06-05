from odoo import fields, api, models, _


class InspectionAdditionalService(models.TransientModel):
    """Inspection Additional Services"""
    _name = 'inspection.additional.service'
    _description = 'Inspection Additional Services'
    _rec_name = 'inspection_id'

    inspection_id = fields.Many2one(comodel_name='vehicle.inspection')
    type = fields.Selection([('service', 'Only Service'), ('service_part', 'Services + Parts')],
                            default='service')
    service_ids = fields.Many2many(comodel_name='product.product',
                                   domain="[('detailed_type','=','service')]",
                                   string='Services')
    service_tax_ids = fields.Many2many(comodel_name='account.tax', string="Service Taxes")
    service_part_ids = fields.One2many(comodel_name='additional.service.part.line',
                                       inverse_name='additional_service_id')

    # Default Get
    @api.model
    def default_get(self, fields):
        """Default get"""
        res = super(InspectionAdditionalService, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['inspection_id'] = active_id
        return res

    def action_add_additional_services(self):
        """Additional Services"""
        if not self.service_ids:
            return

        if self.type == 'service_part' and not self.service_part_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Please add parts !'),
                    'sticky': False,
                }}

        inspection_id = self.inspection_id.id
        vehicle_health_report_id = self.inspection_id.vehicle_health_report_id.id
        parts_to_create = []

        for service in self.service_ids:
            required_service_id = self._process_additional_service(service, inspection_id,
                                                                   vehicle_health_report_id)
            if self.type == 'service_part':
                for part in self.service_part_ids.filtered(lambda p: p.service_id.id == service.id):
                    parts_to_create.append(
                        self._prepare_additional_service_part(part, required_service_id,
                                                              inspection_id,
                                                              vehicle_health_report_id))
        # Batch create services and parts
        if parts_to_create:
            self.env['vehicle.required.parts'].create(parts_to_create)

        self.inspection_id.update_quot_mail = True

    def _process_additional_service(self, service, inspection_id, vehicle_health_report_id):
        """Process Additional Services"""
        return self.env['vehicle.required.services'].create({
            'inspection_id': inspection_id,
            'vehicle_health_report_id': vehicle_health_report_id,
            'product_id': service.id,
            'name': service.name,
            'estimate_time': service.estimate_time,
            'is_additional_service': True,
            'price': service.lst_price,
            'tax_ids': [(6, 0, self.service_tax_ids.ids)] if self.service_tax_ids else [],
        })

    def _prepare_additional_service_part(self, part, required_service_id, inspection_id,
                                         vehicle_health_report_id):
        """Prepare Additional Services Parts for Batch Creation"""
        return {
            'inspection_id': inspection_id,
            'vehicle_health_report_id': vehicle_health_report_id,
            'product_id': part.product_id.id,
            'name': part.name,
            'qty': part.qty,
            'price': part.price,
            'tax_ids': [(6, 0, part.tax_ids.ids)] if part.tax_ids else [],
            'service_id': required_service_id.id,
            'is_additional_part': True,
        }

    def action_add_additional_services(self):
        """Additional Services"""
        for data in self.service_ids:
            required_service_id = self._process_additional_service(data)
            if self.type == 'service_part':
                for part in self.service_part_ids.filtered(lambda p: p.service_id.id == data.id):
                    self._process_additional_service_part(part, required_service_id)
    
    def _process_additional_service(self, data):
        """Process Additional Services"""
        service_id = self.env['vehicle.required.services'].create({
            'inspection_id': self.inspection_id.id,
            'vehicle_health_report_id': self.inspection_id.vehicle_health_report_id.id,
            'product_id': data.id,
            'name': data.name,
            'estimate_time': data.estimate_time,
            'is_additional_service': True
        })
        return service_id
    
    def _process_additional_service_part(self, part, required_service_id):
        """Process Additional Services Parts"""
        self.env['vehicle.required.parts'].create({
            'inspection_id': self.inspection_id.id,
            'vehicle_health_report_id': self.inspection_id.vehicle_health_report_id.id,
            'product_id': part.product_id.id,
            'name': part.name,
            'qty': part.qty,
            'price': part.price,
            'tax_ids': [(6, 0, part.tax_ids.ids)] if part.tax_ids else [],
            'service_id': required_service_id.id,
            'is_additional_part': True,
        })


class AdditionalServicePartLine(models.TransientModel):
    """Additional Service Part Line"""
    _name = 'additional.service.part.line'
    _description = 'Additional Service Part Line'

    additional_service_id = fields.Many2one(comodel_name='inspection.additional.service')
    product_id = fields.Many2one(comodel_name='product.product', string="Part",
                                 domain="[('detailed_type','=','product')]")
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(comodel_name='res.currency', related='company_id.currency_id',
                                  string='Currency')
    name = fields.Char(string="Description")
    qty = fields.Float(string="Qty", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    price = fields.Monetary(string="Unit Price")
    tax_ids = fields.Many2many(comodel_name='account.tax', string="Taxes")
    tax_amount = fields.Monetary(string="Tax Amount", compute="_compute_total_amount")
    untaxed_amount = fields.Monetary(string="Untaxed Amount", compute="_compute_total_amount")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount")
    services_ids = fields.Many2many(related="additional_service_id.service_ids", string="Services")
    service_id = fields.Many2one(comodel_name='product.product', string="Service",
                                 domain="[('id','in',services_ids)]")

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
