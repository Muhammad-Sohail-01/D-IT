from odoo import fields, api, models, _


class VehiclePartsPicking(models.Model):
    _inherit = 'stock.picking'

    job_card_id = fields.Many2one('vehicle.inspection', string="Job Card")
    is_additional_part = fields.Boolean(string="Additional Part")
    additional_part_ids = fields.Many2many('vehicle.required.parts', string="Additional")

    def button_validate(self):
        res = super(VehiclePartsPicking, self).button_validate()
        if self.job_card_id:
            self.send_job_card_validate_mail()
        return res

    
    # def button_validate(self):
    #     res = super(VehiclePartsPicking, self).button_validate()
        # if self.is_additional_part:
        #     for data in self.move_ids_without_package:
        #         if data.additional_part_id:
        #             data.additional_part_id.action_material_arrived()
        # for rec in self.additional_part_ids:
        #     if rec.additional_part_status == 'part_request':
        #         rec.additional_part_status = 'part_received'
        #         rec.additional_part_id.status = 'arrived'
        # if self.job_card_id:
        #     self.send_job_card_validate_mail()
        #     for data in self.move_ids:
        #         svl_vals = data.product_id._prepare_out_svl_vals(data.product_uom_qty,
        #                                                          data.company_id)
        #         self.env['stock.valuation.layer'].create(
        #             {'product_id': data.product_id.id,
        #              'value': svl_vals.get('unit_cost') * svl_vals.get('quantity'),
        #              'unit_cost': svl_vals.get('unit_cost') if svl_vals.get('unit_cost') else 0,
        #              'quantity': svl_vals.get('quantity') if svl_vals.get('quantity') else 0,
        #              'remaining_qty': svl_vals.get('remaining_qty') if svl_vals.get(
        #                  'remaining_qty') else 0,
        #              'stock_move_id': data.id,
        #              'company_id': self.env.company.id,
        #              'description': f"{self.name} - {data.product_id.name}"})
        # return res

         

    def send_job_card_validate_mail(self):
        template_id = self.env.ref(
            'tk_vehicle_management.delivery_order_validate_mail_template').sudo()
        self.env['mail.template'].sudo().browse(template_id.id).with_context({
            'is_additional': True if self.is_additional_part else False,
            'order_no': self.name,
            'responsible': self.env.user.name,
        }).send_mail(self.job_card_id.id, force_send=True)

    class VehicleStockMove(models.Model):
        _inherit = 'stock.move'

        additional_part_id = fields.Many2one('vehicle.required.parts', string="Additional Part")
