from odoo import models, fields, api


class AvailableSerialNumbers (models.Model):
    _name = 'available.serial.numbers'
    _description = 'Available Serial Numbers Across Companies'

    product_id = fields.Many2one ('product.product', string='Product', required=True)
    source_company_id = fields.Many2one ('res.company', string='Source Company', required=True)
    serial_number = fields.Char ('Serial Number', required=True)
    # Changed to use stock.production.lot instead of stock.lot
    lot_id = fields.Many2one ('stock.production.lot', string='Lot/Serial Number')
    is_available = fields.Boolean ('Available', default=True)

    @api.model
    def refresh_available_serials(self):
        """Refresh the available serial numbers list"""
        self.search ([]).unlink ()  # Clear existing records

        companies = self.env['res.company'].search ([])

        for company in companies:
            self = self.with_company (company)

            lots = self.env['stock.production.lot'].search ([
                ('product_id.tracking', '=', 'serial'),
                ('quant_ids.quantity', '>', 0),
                ('quant_ids.location_id.usage', '=', 'internal')
            ])

            vals_list = []
            for lot in lots:
                vals_list.append ({
                    'product_id'       : lot.product_id.id,
                    'source_company_id': company.id,
                    'serial_number'    : lot.name,
                    'lot_id'           : lot.id,
                    'is_available'     : True,
                })

            if vals_list:
                self.create (vals_list)