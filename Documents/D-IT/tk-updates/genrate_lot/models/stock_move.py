# # -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet
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
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.quantity for move in self}

        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        # Once the quantities are assigned, we want to find a better destination location thanks
        # to the putaway rules. This redirection will be applied on moves of `moves_to_redirect`.
        moves_to_redirect = OrderedSet()
        moves_to_assign = self
        if not force_qty:
            moves_to_assign = moves_to_assign.filtered(
                lambda m: not m.picked and m.state in ['confirmed', 'waiting', 'partially_available']
            )
        moves_mto = moves_to_assign.filtered(lambda m: m.move_orig_ids and not m._should_bypass_reservation())
        quants_cache = self.env['stock.quant']._get_quants_cache_by_products_locations(moves_mto.product_id,
                                                                                       moves_mto.location_id)
        for move in moves_to_assign:
            rounding = roundings[move]
            if not force_qty:
                missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            else:
                missing_reserved_uom_quantity = force_qty
            if float_compare(missing_reserved_uom_quantity, 0, precision_rounding=rounding) <= 0:
                assigned_moves_ids.add(move.id)
                continue
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity,
                                                                           move.product_id.uom_id,
                                                                           rounding_method='HALF-UP')

            if move._should_bypass_reservation():
                # create the move line(s) but do not impact quants
                if move.move_orig_ids:
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids,
                                                                          partially_available_moves_ids)
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

                if missing_reserved_quantity and move.product_id.tracking == 'serial' and (
                        move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                elif missing_reserved_quantity:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                                       ml.location_id == move.location_id and
                                                                       ml.location_dest_id == move.location_dest_id and
                                                                       ml.picking_id == move.picking_id and
                                                                       not ml.picked and
                                                                       not ml.lot_id and
                                                                       not ml.result_package_id and
                                                                       not ml.package_id and
                                                                       not ml.owner_id)
                    if to_update:
                        to_update[0].quantity += move.product_id.uom_id._compute_quantity(
                            missing_reserved_quantity, move.product_uom, rounding_method='HALF-UP')
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves_ids.add(move.id)
                moves_to_redirect.add(move.id)
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding) and not force_qty:
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    taken_quantity = move._update_reserved_quantity(need, move.location_id,
                                                                    package_id=forced_package_id, strict=False)
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    moves_to_redirect.add(move.id)
                    if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids,
                                                                          partially_available_moves_ids)
                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.quantity_product_uom):
                        if available_move_lines.get(
                                (move_line.location_id, move_line.lot_id, move_line.package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.package_id,
                                                  move_line.owner_id)] -= move_line.quantity_product_uom
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('quantity_product_uom'))
                        taken_quantity = move.with_context(quants_cache=quants_cache)._update_reserved_quantity(
                            min(quantity, need), location_id, None, lot_id, package_id, owner_id)
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        moves_to_redirect.add(move.id)
                        if float_is_zero(need - taken_quantity, precision_rounding=rounding):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty
        data_list = []
        for ldata in move_line_vals_list:
            if not ldata.get('lot_id'):
                move_data = self.env['stock.move'].browse(ldata.get('move_id'))
                if move_data.purchase_line_id:
                    for i in range(int(ldata.get('quantity'))):
                        lot_line = self.env['stock.lot'].search([('product_id', '=', move_data.product_id.id)])
                        lot = ''

                        if lot_line:
                            last_lot_line_id = max(lot_line.ids)
                            last_lot_line = self.env['stock.lot'].browse(last_lot_line_id)

                            # Extract the last 5 digits from the end of the last lot name
                            name = last_lot_line[0].name
                            numeric_part = re.search(r'(\d{5})$', name)  # Match exactly the last 5 digits
                            if numeric_part:
                                # Increment the 5-digit numeric part
                                next_number = str(int(numeric_part.group()) + 1).zfill(5)
                            else:
                                # Default to '00001' if no numeric part is found
                                next_number = '00001'

                            # Format the lot number
                            lot = (
                                f"{move_data.purchase_line_id.order_id.name.lstrip('P')}"
                                f"{move_data.product_id.partno_line_id.part_internal_no or ''}"
                                f"-{(move_data.product_id.partno_line_id.part_type or '').upper()}-"
                                f"{next_number}"
                            )
                        else:
                            lot = (
                                f"{move_data.purchase_line_id.order_id.name.lstrip('P')}"
                                f"{move_data.product_id.partno_line_id.part_internal_no or ''}"
                                f"-{(move_data.product_id.partno_line_id.part_type or '').upper()}-"
                                "00001"
                            )

                        d = ldata.copy()

                        if lot:
                            lots_to_create_vals = [
                                {'product_id': move_data.product_id.id, 'name': lot, 'company_id': self.env.company.id}]
                            lot_data_id = self.env['stock.lot'].create(lots_to_create_vals)
                            d.update({'lot_id': lot_data_id.id})
                        d.update({'quantity': 1})
                        data_list.append(d)
                else:
                    data_list.append(ldata)
            else:
                data_list.append(ldata)
        self.env['stock.move.line'].create(data_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
        if not self.env.context.get('bypass_entire_pack'):
            self.picking_id._check_entire_pack()
        StockMove.browse(moves_to_redirect).move_line_ids._apply_putaway_strategy()
