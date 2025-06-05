from odoo import fields, api, models


class VehicleCancelInspection(models.TransientModel):
    """Cancel Inspection Confirmation"""
    _name = 'vehicle.cancel.inspection'
    _description = 'Vehicle Job Card Cancel'

    inspection_id = fields.Many2one(comodel_name='vehicle.inspection', string="Job Card")
    is_return_part = fields.Boolean(string="Return Completed Part Order ?",
                                    help="This option create Return Order if there any part order is completed.")
    is_cancel_part = fields.Boolean(string="Cancel Pending Part Order ?", default=True,
                                    help="This Options will Cancel & Delete Pending Part Order whose state are in Draft, Waiting, Ready and Assigned")

    # Default Get
    @api.model
    def default_get(self, fields):
        """Default Get"""
        res = super(VehicleCancelInspection, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['inspection_id'] = active_id
        return res

    def action_cancel_job_card(self):
        """Cancel job card"""
        if self.is_cancel_part:
            self._process_cancel_parts_orders()
        if self.is_return_part:
            self._process_return_parts_orders()
        self.inspection_id.action_status_cancel()

    def _process_return_parts_orders(self):
        """Process Return Orders"""
        delivery_orders = self.env['stock.picking'].sudo().search(
            [('job_card_id', '=', self.inspection_id.id), ('state', '=', 'done')])
        if delivery_orders:
            for rec in delivery_orders.filtered(lambda r: not r.return_ids):
                return_id = self.env['stock.return.picking'].sudo().create({
                    'picking_id': rec.id
                })
                return_id._create_returns()

    def _process_cancel_parts_orders(self):
        """Cancel and Delete Orders"""
        delivery_orders = self.env['stock.picking'].sudo().search(
            [('job_card_id', '=', self.inspection_id.id), ('picking_type_code', '!=', 'incoming'),
             ('state', 'not in', ['done', 'cancel'])])
        if delivery_orders:
            for rec in delivery_orders:
                rec.action_cancel()
