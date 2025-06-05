from odoo import api, fields, models

class TaskAssignInherit(models.TransientModel):
    _inherit = 'task.assignation'
    _description = "Task Assignation Inherit"


    
    # leaders_ids = fields.Many2many('hr.employee', string="Team Leaders",
    #                                 domain=[('team_leader', '=', True)])
    # technician_ids = fields.Many2many('hr.employee', 'task_assign_technician_rel',
    #                                   'task_assign_technician_id',
    #                                   'task_assign_user_technician_id', string="Technicians",
    #                                    domain=[('technician', '=', True)])
                                      
    