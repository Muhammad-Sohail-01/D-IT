# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SerialNumberSelectionWizard (models.TransientModel):
    _name = 'serial.number.selection.wizard'
    _description = 'Serial Number Selection for Inter-company Transfer'

    move_id = fields.Many2one ('stock.move', string='Stock Move', required=True)
    source_company_id = fields.Many2one ('res.company', string='Source Company')
    product_id = fields.Many2one ('product.product', related='move_id.product_id')
    quantity_needed = fields.Float (related='move_id.product_uom_qty')

    available_lot_ids = fields.Many2many (
        'stock.lot',
        string='Available Serial Numbers',
        domain="[('product_id', '=', product_id)]"
    )
    selected_lot_ids = fields.Many2many (
        'stock.lot',
        'serial_selection_rel',
        'wizard_id',
        'lot_id',
        string='Selected Serial Numbers'
    )

    @api.onchange ('available_lot_ids')
    def _onchange_available_lot_ids(self):
        """Update domain based on available lots"""
        return {
            'domain': {
                'selected_lot_ids': [('id', 'in', self.available_lot_ids.ids)]
            }
        }

    def action_confirm_selection(self):
        """Create move lines with selected serial numbers"""
        self.ensure_one ()

        if len (self.selected_lot_ids) != int (self.quantity_needed):
            raise ValidationError (
                f"Please select exactly {int (self.quantity_needed)} serial numbers."
            )

        # Create move lines
        move_lines = []
        for lot in self.selected_lot_ids:
            move_lines.append ({
                'move_id'         : self.move_id.id,
                'product_id'      : self.product_id.id,
                'product_uom_id'  : self.move_id.product_uom.id,
                'location_id'     : self.move_id.location_id.id,
                'location_dest_id': self.move_id.location_dest_id.id,
                'lot_id'          : lot.id,
                'quantity'        : 1,
            })

        # Create move lines and update move state
        self.env['stock.move.line'].create (move_lines)
        self.move_id.write ({'state': 'assigned'})

        # Update lot company
        self.selected_lot_ids.write ({
            'company_id': self.env.company.id
        })

        return {'type': 'ir.actions.act_window_close'}
