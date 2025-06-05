from odoo import models

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_done(self):
        # Call the super to mark the current activity as done
        result = super(MailActivity, self).action_done()

        # Identify other activities for the same record and activity type
        related_activities = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),# Same record ID
            ('activity_type_id', '=', self.env.ref('tk_vehicle_management.mail_act_print_gate_pass_approval').id),  # Same activity 
            ('state', '=', 'planned')  # Only planned activities
        ])
        related_activities.action_feedback(feedback="Aprrove")

        for act in related_activities:
        
        # Mark other activities as done
            act.action_done()
        

        return result
