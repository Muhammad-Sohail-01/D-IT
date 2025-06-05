from odoo import api, fields, models


class AssignTeamInherit(models.TransientModel):
    _inherit = 'assign.team'
    _description = 'Assign Team'

    # leaders_ids = fields.Many2many('hr.employee', string="Team Leaders",
    #                                domain="[('id','in',team_leaders_ids)]")
    # technician_ids = fields.Many2many('hr.employee', 'assign_technician_rel',
    #                                   'assign_technician_id',
    #                                   'assign_user_technician_id',
    #                                   string="Technicians",
    #                                   domain="[('id','in',team_technician_ids),('technician','=',True)]")

    registration_no = fields.Char(string="Registration No")


    @api.model
    def default_get(self, fields):
        res = super(AssignTeamInherit, self).default_get(fields)
        active_id = self._context.get('active_id')
        inspection_id = self.env['vehicle.inspection'].browse(active_id)

        res['task_title'] = str(inspection_id.name) + " 's Task"
        res['registration_no'] = inspection_id.registration_no

        res['allocated_hours'] = inspection_id.selected_services_time_total


        tag_ids = []
        for customer_tag in inspection_id.customer_tag_ids:
            # Check if the tag already exists in project.tags
            existing_tag = self.env['project.tags'].search([('name', '=', customer_tag.name)], limit=1)

            if existing_tag:
                tag_ids.append(existing_tag.id)
            else:
                # Create a new tag if it doesn't exist
                new_tag = self.env['project.tags'].create({'name': customer_tag.name})
                tag_ids.append(new_tag.id)

        if tag_ids:
            res['tag_ids'] = [(6, 0, tag_ids)]
        else:
            res['tag_ids'] = [(5,)]

        return res


    def action_assign_team(self):
        # Call the original method
        result = super(AssignTeamInherit, self).action_assign_team()

        # Assuming you have access to the context and inspection_id
        active_id = self._context.get('active_id')
        inspection_id = self.env['vehicle.inspection'].browse(active_id)

        # Get the task created by the original method
        task_id = inspection_id.vehicle_health_report_id.task_id

        # Update the task with the registration number
        if task_id and inspection_id.registration_no:
            task_id.car_plate_number = inspection_id.registration_no
            task_id.service_adviser_id = inspection_id.service_adviser_id.id
            task_id.user_ids = False


        return result

