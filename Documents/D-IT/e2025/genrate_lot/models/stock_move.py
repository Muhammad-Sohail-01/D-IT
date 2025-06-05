# # -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet
from odoo.exceptions import ValidationError
import re


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_state = fields.Selection(
        related='picking_id.state',
        string='Picking State',
        store=True,
    )

    

    def _action_assign(self, force_qty=False):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `reserved_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        reserved_availability = {move: move.quantity for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        moves_to_redirect = OrderedSet()
        moves_to_assign = self
    
        if not force_qty:
            moves_to_assign = moves_to_assign.filtered(
                lambda m: not m.picked and m.state in ['confirmed', 'waiting', 'partially_available']
            )
        
        for move in moves_to_assign:
            rounding = roundings[move]
            if not force_qty:
                missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            else:
                missing_reserved_uom_quantity = force_qty
            
            if float_compare(missing_reserved_uom_quantity, 0, precision_rounding=rounding) <= 0:
                assigned_moves_ids.add(move.id)
                continue
            
            missing_reserved_quantity = move.product_uom._compute_quantity(
                missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP'
            )
            
            if move._should_bypass_reservation():
                # Handle bypass reservation logic
                if move.move_orig_ids:
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids, partially_available_moves_ids)
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        qty_added = min(missing_reserved_quantity, quantity)
                        move_line_vals = move._prepare_move_line_vals(qty_added)
                        move_line_vals.update({
                            'location_id': location_id.id,
                            'lot_id': lot_id.id,
                            'lot_name': lot_id.name,
                            'owner_id': owner_id.id,
                            'package_id': package_id.id,
                        })
                        move_line_vals_list.append(move_line_vals)
                        missing_reserved_quantity -= qty_added
                        if float_is_zero(missing_reserved_quantity, precision_rounding=move.product_id.uom_id.rounding):
                            break
                
                if missing_reserved_quantity:
                    if move.product_id.tracking == 'serial' and (
                        move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots
                    ):
                        for i in range(0, int(missing_reserved_quantity)):
                            move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                
                assigned_moves_ids.add(move.id)
                moves_to_redirect.add(move.id)
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding) and not force_qty:
                    assigned_moves_ids.add(move.id)
        
        # Lot creation and data handling
        data_list = []
        for ldata in move_line_vals_list:
            move_id = ldata.get('move_id')
            move_data = self.env['stock.move'].browse(move_id)
            if len(move_data) != 1:
                raise ValidationError("Expected a single stock.move record.")
            if move_data.product_id.detailed_type != 'product':  # Check if the product type is not storable
                continue
            
            if not ldata.get('lot_id') and move_data.purchase_line_id:
                # Ensure the product is storable before lot/serial number creation
                if move_data.product_id.type != 'product':
                    raise ValidationError(
                        f"Lot/Serial numbers can only be created for storable products. "
                        f"Product '{move_data.product_id.display_name}' is of type '{move_data.product_id.type}'."
                    )
                lot_line = self.env['stock.lot'].search([('product_id', '=', move_data.product_id.id)])
                for i in range(int(ldata.get('quantity'))):
                    if lot_line:
                        last_lot_line_id = max(lot_line.ids)
                        last_lot_line = self.env['stock.lot'].browse(last_lot_line_id)
                        name = last_lot_line.name
                        numeric_part = re.search(r'(\d{5})$', name)
                        next_number = str(int(numeric_part.group()) + 1).zfill(5) if numeric_part else '00001'
                        lot = f"{move_data.purchase_line_id.order_id.name.lstrip('P')}" \
                              f"{move_data.part_number_id.part_internal_no or ''}" \
                              f"-{(move_data.part_number_id.part_type or '').upper()}-{next_number}"
                    else:
                        lot = f"{move_data.purchase_line_id.order_id.name.lstrip('P')}" \
                              f"{move_data.part_number_id.part_internal_no or ''}" \
                              f"-{(move_data.part_number_id.part_type or '').upper()}-00001"
            
                    lots_to_create_vals = [{'product_id': move_data.product_id.id, 'name': lot, 'company_id': self.env.company.id}]
                    lot_data_id = self.env['stock.lot'].create(lots_to_create_vals)
                    d = ldata.copy()
                    d.update({'lot_id': lot_data_id.id, 'quantity': 1})
                    data_list.append(d)
            else:
                data_list.append(ldata)
        
        # Create stock move lines
        self.env['stock.move.line'].create(data_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
    
        if not self.env.context.get('bypass_entire_pack'):
            self.picking_id._check_entire_pack()
        StockMove.browse(moves_to_redirect).move_line_ids._apply_putaway_strategy()

