from odoo import api, fields, models, _
from markupsafe import Markup


class InspectionRejectReason(models.TransientModel):
    _name = 'inspection.reject.reason'
    _description = 'Inspection Reject Reason'

    name = fields.Text(string="Reject Reason")

    def action_reject_inspection(self):
        active_id = self._context.get('active_id')
        reject = self._context.get('reject')
        inspection_id = self.env['vehicle.inspection'].browse(active_id)
        if self.name and reject == 'concern':
            body = Markup('<strong>Concern Reject Reason : </strong><br/>')
            body = body + str(self.name)
            inspection_id.message_post(body=body, message_type="notification",
                                       partner_ids=[self.env.user.partner_id.id])
            inspection_id.status = 'concern_reject'
        if self.name and reject == 'quot':
            body = Markup('<strong>Quotation Reject Reason : </strong><br/>')
            body = body + str(self.name)
            inspection_id.message_post(body=body, message_type="notification",
                                       partner_ids=[self.env.user.partner_id.id])
            inspection_id.action_status_reject()
        if self.name and reject == 'qc_check':
            task_line_id = self.env['inspection.qc.check'].browse(active_id)
            body = Markup('<strong>QC Reject Reason : </strong><hr class="mb-1 mt-1"/>')
            body = body + str(self.name)
            body_inspection = Markup(
                'Task : <strong>' + str(
                    task_line_id.task_id.name) + '(Qc Check)</strong><br/>Reject Reason : <br/><strong>' + str(
                    self.name) + '</strong>')
            task_line_id.is_reject = True

            task_line_id.inspection_id.message_post(body=body_inspection,
                                                    message_type="notification",
                                                    partner_ids=[self.env.user.partner_id.id])
            # Process Task QC Reject
            task_line_id.task_id.action_vehicle_task_qc_reject(reject_reason=self.name)

        if self.name and reject == 'part_reject':
            part_line_id = self.env['vehicle.required.parts'].browse(active_id)
            if not part_line_id.service_id.service_selected:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Service Selection Pending !'),
                        'message': _(
                            'The related service for this part has not been selected yet.'),
                        'sticky': False,
                    }}
            body = Markup('Additional Part Confirmation : <br/>Part Name : <strong>' + str(
                part_line_id.product_id.name) + '<br/>Reject Reason : </strong><hr class="mb-1 mt-1"/>')
            body = body + str(self.name)
            part_line_id.vehicle_health_report_id.inspection_id.message_post(body=body,
                                                                             message_type="notification",
                                                                             partner_ids=[
                                                                                 self.env.user.partner_id.id])
            if part_line_id.additional_part_id:
                part_line_id.additional_part_id.task_id.message_post(body=body,
                                                                     message_type="notification",
                                                                     partner_ids=[
                                                                         self.env.user.partner_id.id])
            part_line_id.action_reject_part()
        if self.name and reject == 'warranty':
            warranty_id = self.env['vehicle.warranty'].browse(active_id)
            body = Markup('<strong>Cancel Reason</strong> : <br/>')
            body = body + str(self.name)
            warranty_id.message_post(body=body,
                                     message_type="notification",
                                     partner_ids=[self.env.user.partner_id.id])
            warranty_id.action_cancel_vehicle_warranty()
