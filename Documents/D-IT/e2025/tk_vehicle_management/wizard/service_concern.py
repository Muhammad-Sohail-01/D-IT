from odoo import api, fields, models


class ServiceConcern(models.TransientModel):
    _name = 'service.concern'
    _description = 'Service Concern'
    _rec_name = 'concern'

    concern = fields.Text(string='Concern')
    cause = fields.Text(string='Cause')
    correction = fields.Text(string='Correction')
    service_id = fields.Many2one('vehicle.required.services', string='Service')

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(ServiceConcern, self).default_get(fields)
        active_id = self._context.get('active_id')
        service_id = self.env['vehicle.required.services'].browse(active_id)
        res['service_id'] = active_id
        res['concern'] = service_id.concern
        res['cause'] = service_id.cause
        res['correction'] = service_id.correction
        return res

    def update_service_concern(self):
        self.service_id.write({'concern': self.concern, 'cause': self.cause, 'correction': self.correction})
