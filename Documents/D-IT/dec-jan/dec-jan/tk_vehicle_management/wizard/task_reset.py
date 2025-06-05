from odoo import fields, api, models
from markupsafe import Markup


class VehicleTaskReset(models.TransientModel):
    """Vehicle job card task status reset"""
    _name = 'vehicle.task.reset'
    _description = 'Vehicle Task Reset'

    inspection_id = fields.Many2one(comodel_name='vehicle.inspection', string="Inspection")
    is_reset_all_task = fields.Boolean(string="Reset All Task")
    task_ids = fields.Many2many(comodel_name='project.task',
                                string="Tasks",
                                domain="""[('inspection_id', '=', inspection_id),
                                            ('is_inspection_task','=',False),
                                            ('task_state','=','complete')]""")

    # Default Get
    @api.model
    def default_get(self, fields):
        """Default Get"""
        res = super(VehicleTaskReset, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['inspection_id'] = active_id
        return res

    def action_reset_service_task_status(self):
        """Process job cars service task reset"""
        if self.is_reset_all_task:
            tasks = self.inspection_id.inspection_required_service_ids.mapped('task_id')
            tasks.action_reset_draft()
            self.action_task_reset_notification(task_ids=tasks)
            if self.inspection_id.status == 'parts_available':
                self.inspection_id.status = 'in_repair'
        else:
            self.task_ids.action_reset_draft()
            self.action_task_reset_notification(task_ids=self.task_ids)
            if self.inspection_id.status == 'parts_available':
                self.inspection_id.status = 'in_repair'

    def action_task_reset_notification(self, task_ids):
        job_card_log = Markup(
            f"The following task has been opened : <br/><strong>{', '.join(task_ids.mapped('name'))}</strong")
        self.inspection_id.message_post(body=job_card_log, message_type="notification",
                                        partner_ids=[self.env.user.partner_id.id])
        for data in task_ids:
            data.message_post(body="Task Opened", message_type="notification",
                              partner_ids=[self.env.user.partner_id.id])
