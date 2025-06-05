from odoo import api, fields, models, _
from markupsafe import Markup
from collections import defaultdict

class VehicleInspectionTaskInheritStage(models.Model):
    _inherit = 'project.task.stage.personal'


    # user_id = fields.Many2one('hr.employee')


class VehicleInspectionTaskInherit(models.Model):
    _inherit = 'project.task'

    # leaders_ids = fields.Many2many('hr.employee', string="Team Leaders",
    #                                domain="[('id','in',team_leaders_ids)]")

    team_technician_id = fields.Many2many(related="team_id.technician_ids",
                                        string="Team Leader")
    car_plate_number = fields.Char(string="Plate No")
    bay = fields.Many2one('vehicle.bay', string="Bay")



    portal_user_group_id = fields.Many2many(
        'res.groups',
        string='Portal User Group',
        compute='_compute_portal_user_group',
        store=True,  # This field is computed and doesn't need to be stored
    )

    @api.depends('team_id')
    def _compute_portal_user_group(self):
        portal_group = self.env.ref('base.group_portal')
        for record in self:
            record.portal_user_group_id = [(6, 0, [portal_group.id])] 

    

    # Existing fields...

    user_ids = fields.Many2many(
        'res.users',
        relation='project_task_user_rel',
        column1='task_id',
        column2='user_id',
        string='Assignees',
        tracking=True,
        
        
    )
    


    def action_request_qc_check(self):
        # Call the original method logic
        self.task_state = 'complete'
        res = super(VehicleInspectionTaskInherit, self).action_request_qc_check()

        new_qc_task = self.create({
            'name': f'Quality Check for {self.name}',  # Name the new task
            'project_id': self.project_id.id,  # Link to the same project
            'description': 'Quality Check Task',  # Set a description
            'team_id': self.team_id.id,  # Link to the same team
            'leaders_ids': [(6, 0, self.leaders_ids.ids)],  # Assign leaders
            'parent_id': self.id,  # Link to the original task
            'task_state': 'qc_check',  # Set task state to 'qc_check'
            
        })
        self.task_state = 'complete'
        self._process_inspection_task_status(status_to='complete')
        new_qc_task._process_inspection_task_status(status_to='qc_check')



        # # Optionally, you can send a notification for the new task
        # if new_qc_task:
        #     self.env['mail.template'].sudo().browse(
        #         self.env.ref('tk_vehicle_management.task_qc_check_mail_template').id
        #     ).send_mail(
        #         new_qc_task.id,
        #         email_values={
        #             'email_to': ','.join(self.leaders_ids.mapped('work_email')),
        #             'email_from': self.env.company.sudo().email,
        #         },
        #         force_send=True
        #     )
        #

        return res

    @api.model
    def _default_user_ids(self):
        super(VehicleInspectionTaskInherit, self)._default_user_ids(self)
        return []  # Return an empty list if you want to show all users



    # @api.model
    # def _populate_missing_personal_stages(self):

    #     # Assign the default personal stage for those that are missing
    #     personal_stages_without_stage = self.env['project.task.stage.personal'].sudo().search([
    #         ('task_id', 'in', self.ids),
    #         ('stage_id', '=', False)
    #     ])
        
    #     if personal_stages_without_stage:
    #         user_ids = personal_stages_without_stage.user_id
    #         personal_stage_by_user = defaultdict(lambda: self.env['project.task.stage.personal'])
            
    #         for personal_stage in personal_stages_without_stage:
    #             personal_stage_by_user[personal_stage.user_id] |= personal_stage
                
    #         for user_id in user_ids:
    #             stage = self.env['project.task.type'].sudo().search([('user_id', '=', user_id.id)], limit=1)
                
    #             # In the case no stages have been found, we create the default stages for the user
    #             if not stage:
    #                 # Change from partner_id to user_partner_id
    #                 stages = self.env['project.task.type'].sudo().with_context(
    #                     lang=user_id.user_partner_id.lang,  # Updated line
    #                     default_project_ids=False
    #                 ).create(
    #                     self.with_context(lang=user_id.user_partner_id.lang)._get_default_personal_stage_create_vals(user_id.id)
    #                 )
    #                 stage = stages[0]
                
    #             personal_stage_by_user[user_id].sudo().write({'stage_id': stage.id})














    

















