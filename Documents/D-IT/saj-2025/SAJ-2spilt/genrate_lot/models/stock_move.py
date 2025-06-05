# # -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet
from odoo.exceptions import ValidationError, UserError
import re

class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_state = fields.Selection(
        related='picking_id.state',
        string='Picking State',
        store=True,
    )

    is_intercompany_transfer = fields.Boolean(
        compute='_compute_is_intercompany_transfer',
        store=True
    )


    @api.depends ('purchase_line_id.order_id.partner_id.company_id')
    def _compute_is_intercompany_transfer(self):
        """Determine if this is an inter-company transfer"""
        for move in self:
            if move.purchase_line_id and move.purchase_line_id.order_id:
                partner = move.purchase_line_id.order_id.partner_id
                move.is_intercompany_transfer = bool (partner.company_id)
            else:
                move.is_intercompany_transfer = False

    def _get_available_serial_numbers(self, source_company, product_id, quantity):
        """Get available serial numbers from source company"""
        domain = [
            ('product_id', '=', product_id),
            ('company_id', '=', source_company.id),
            ('quant_ids.quantity', '>', 0),
            ('quant_ids.location_id.usage', '=', 'internal')
        ]
        return self.env['stock.lot'].with_company (source_company.id).search (domain)

    def _sync_serial_numbers_from_so(self):
        """Sync serial numbers from related sale order"""
        self.ensure_one ()
        if not self.is_intercompany_transfer or not self.purchase_line_id:
            return False

        purchase = self.purchase_line_id.order_id
        source_company = purchase.partner_id.company_id

        # Find related SO
        sale_order = self.env['sale.order'].with_company (source_company.id).search ([
            ('company_id', '=', source_company.id),
            ('name', '=', purchase.partner_ref) if purchase.partner_ref else ('id', '=', -1)
        ], limit=1)

        if not sale_order:
            return False

        # Find related delivery
        delivery = self.env['stock.picking'].with_company (source_company.id).search ([
            ('sale_id', '=', sale_order.id),
            ('state', '=', 'done'),
            ('picking_type_code', '=', 'outgoing')
        ], limit=1)

        if not delivery:
            return False

        # Get serial numbers
        delivery_move = delivery.move_ids.filtered (
            lambda m: m.product_id.id == self.product_id.id
        )
        if delivery_move and delivery_move.move_line_ids:
            return delivery_move.move_line_ids.mapped ('lot_id')

        return False

    def _action_assign(self, force_qty=False):
        """Override to handle internal transfers differently"""
        for move in self:
            if not move.is_intercompany_transfer or not move.product_id.tracking == 'serial':
                return super (StockMove, self)._action_assign (force_qty=force_qty)

            # For internal transfers
            source_company = move.purchase_line_id.order_id.partner_id.company_id

            # Try to sync serial numbers from SO first
            synced_lots = move._sync_serial_numbers_from_so ()
            if synced_lots:
                # Create move lines with synced serial numbers
                vals_list = []
                for lot in synced_lots:
                    vals_list.append ({
                        'move_id'         : move.id,
                        'product_id'      : move.product_id.id,
                        'product_uom_id'  : move.product_uom.id,
                        'location_id'     : move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id'          : lot.id,
                        'quantity'        : 1,
                    })
                if vals_list:
                    self.env['stock.move.line'].create (vals_list)
                    move.write ({'state': 'assigned'})
                return

            # If no synced numbers, let user select from available ones
            available_lots = self._get_available_serial_numbers (
                source_company,
                move.product_id.id,
                int (move.product_uom_qty)
            )

            if not available_lots:
                raise ValidationError (
                    f"No available serial numbers found in {source_company.name} "
                    f"for product {move.product_id.display_name}. "
                    f"Please ensure serial numbers exist in source company."
                )

            # Open serial number selection wizard
            return {
                'name'     : 'Select Serial Numbers',
                'type'     : 'ir.actions.act_window',
                'res_model': 'serial.number.selection.wizard',
                'view_mode': 'form',
                'target'   : 'new',
                'context'  : {
                    'default_move_id'          : move.id,
                    'default_source_company_id': source_company.id,
                    'default_available_lot_ids': available_lots.ids,
                }
            }

    def action_serial_number_selection(self):
        self.ensure_one()
        if not self.is_intercompany_transfer:
            raise UserError('Serial number selection is only available for inter-company transfers.')

        source_company = self.purchase_line_id.order_id.partner_id.company_id
        available_lots = self._get_available_serial_numbers(
            source_company,
            self.product_id.id,
            int(self.product_uom_qty)
        )

        if not available_lots:
            raise UserError(
                f"No available serial numbers found in {source_company.name} "
                f"for product {self.product_id.display_name}"
            )

        return {
            'name': 'Select Serial Numbers',
            'type': 'ir.actions.act_window',
            'res_model': 'serial.number.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_product_id': self.product_id.id,
                'default_source_company_id': source_company.id,
                'default_quantity_needed': self.product_uom_qty,
                'default_available_lot_ids': available_lots.ids,
            }
        }

    def _action_assign(self, force_qty=False):
        """Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `reserved_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet ()
        partially_available_moves_ids = OrderedSet ()
        reserved_availability = {move: move.quantity for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        moves_to_redirect = OrderedSet ()
        moves_to_assign = self

        if not force_qty:
            moves_to_assign = moves_to_assign.filtered (
                lambda m: not m.picked and m.state in ['confirmed', 'waiting', 'partially_available']
            )

        for move in moves_to_assign:
            rounding = roundings[move]
            if not force_qty:
                missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            else:
                missing_reserved_uom_quantity = force_qty

            if float_compare (missing_reserved_uom_quantity, 0, precision_rounding=rounding) <= 0:
                assigned_moves_ids.add (move.id)
                continue

            missing_reserved_quantity = move.product_uom._compute_quantity (
                missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP'
            )

            if move._should_bypass_reservation ():
                # Handle bypass reservation logic
                if move.move_orig_ids:
                    available_move_lines = move._get_available_move_lines (assigned_moves_ids,
                                                                           partially_available_moves_ids)
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items ():
                        qty_added = min (missing_reserved_quantity, quantity)
                        move_line_vals = move._prepare_move_line_vals (qty_added)
                        move_line_vals.update ({
                            'location_id': location_id.id,
                            'lot_id'     : lot_id.id,
                            'lot_name'   : lot_id.name,
                            'owner_id'   : owner_id.id,
                            'package_id' : package_id.id,
                        })
                        move_line_vals_list.append (move_line_vals)
                        missing_reserved_quantity -= qty_added
                        if float_is_zero (missing_reserved_quantity,
                                          precision_rounding=move.product_id.uom_id.rounding):
                            break

                if missing_reserved_quantity:
                    if move.product_id.tracking == 'serial' and (
                            move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots
                    ):
                        for i in range (0, int (missing_reserved_quantity)):
                            move_line_vals_list.append (move._prepare_move_line_vals (quantity=1))
                    else:
                        move_line_vals_list.append (move._prepare_move_line_vals (quantity=missing_reserved_quantity))

                assigned_moves_ids.add (move.id)
                moves_to_redirect.add (move.id)
            else:
                if float_is_zero (move.product_uom_qty, precision_rounding=move.product_uom.rounding) and not force_qty:
                    assigned_moves_ids.add (move.id)

        # Process move lines
        data_list = []
        for ldata in move_line_vals_list:
            move_id = ldata.get ('move_id')
            move_data = self.env['stock.move'].browse (move_id)
            if len (move_data) != 1:
                raise ValidationError ("Expected a single stock.move record.")
            if move_data.product_id.detailed_type != 'product':
                continue

            if not ldata.get ('lot_id') and move_data.purchase_line_id and move_data.product_id.tracking == 'serial':
                # Check if this is an inter-company transfer
                vendor_company = move_data.purchase_line_id.order_id.partner_id.company_id
                odoo_companies = self.env['res.company'].search ([])
                is_internal_purchase = vendor_company and vendor_company.id in odoo_companies.ids

                if is_internal_purchase:
                    # Try to sync serial numbers from SO
                    synced_lots = move_data._sync_serial_numbers_from_so ()
                    if synced_lots:
                        for lot in synced_lots:
                            d = ldata.copy ()
                            d.update ({'lot_id': lot.id, 'quantity': 1})
                            data_list.append (d)
                        continue  # Skip to next ldata if we found synced lots

                    # If no synced lots, let user select from available ones
                    source_company = move_data.purchase_line_id.order_id.partner_id.company_id
                    available_lots = move_data._get_available_serial_numbers (
                        source_company,
                        move_data.product_id.id,
                        int (ldata.get ('quantity'))
                    )

                    return {
                        'name'     : 'Select Serial Numbers',
                        'type'     : 'ir.actions.act_window',
                        'res_model': 'serial.number.selection.wizard',
                        'view_mode': 'form',
                        'target'   : 'new',
                        'context'  : {
                            'default_move_id'          : move_data.id,
                            'default_source_company_id': source_company.id,
                            'default_available_lot_ids': available_lots.ids,
                            'default_quantity_needed'  : ldata.get ('quantity'),
                        }
                    }
                else:
                    # Your existing logic for normal vendor purchases
                    if move_data.product_id.type != 'product':
                        raise ValidationError (
                            f"Lot/Serial numbers can only be created for storable products. "
                            f"Product '{move_data.product_id.display_name}' is of type '{move_data.product_id.type}'."
                        )

                    lot_line = self.env['stock.lot'].search ([('product_id', '=', move_data.product_id.id)])
                    for i in range (int (ldata.get ('quantity'))):
                        if lot_line:
                            last_lot_line_id = max (lot_line.ids)
                            last_lot_line = self.env['stock.lot'].browse (last_lot_line_id)
                            name = last_lot_line.name
                            numeric_part = re.search (r'(\d{5})$', name)
                            next_number = str (int (numeric_part.group ()) + 1).zfill (5) if numeric_part else '00001'
                            lot = f"{move_data.purchase_line_id.order_id.name.lstrip ('P')}" \
                                  f"{move_data.part_number_id.part_internal_no or ''}" \
                                  f"-{(move_data.part_number_id.part_type or '').upper ()}-{next_number}"
                        else:
                            lot = f"{move_data.purchase_line_id.order_id.name.lstrip ('P')}" \
                                  f"{move_data.part_number_id.part_internal_no or ''}" \
                                  f"-{(move_data.part_number_id.part_type or '').upper ()}-00001"

                        lots_to_create_vals = [{
                            'product_id': move_data.product_id.id,
                            'name'      : lot,
                            'company_id': self.env.company.id
                        }]
                        lot_data_id = self.env['stock.lot'].create (lots_to_create_vals)
                        d = ldata.copy ()
                        d.update ({'lot_id': lot_data_id.id, 'quantity': 1})
                        data_list.append (d)
            else:
                data_list.append (ldata)

        # Create stock move lines
        self.env['stock.move.line'].create (data_list)
        StockMove.browse (partially_available_moves_ids).write ({'state': 'partially_available'})
        StockMove.browse (assigned_moves_ids).write ({'state': 'assigned'})

        if not self.env.context.get ('bypass_entire_pack'):
            self.picking_id._check_entire_pack ()
        StockMove.browse (moves_to_redirect).move_line_ids._apply_putaway_strategy ()