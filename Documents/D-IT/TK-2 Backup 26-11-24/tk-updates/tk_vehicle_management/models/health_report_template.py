from odoo import fields, api, models


class HealthReportTemplate(models.Model):
    _name = 'health.report.template'
    _description = 'Health Report Template'

    name = fields.Char(string='Title')

    # Inspection
    inner_body_inspection = fields.Boolean(string="Interior")
    outer_body_inspection = fields.Boolean(string="Exterior")
    mechanical_condition = fields.Boolean(string="Under Hood / Mechanical")
    vehicle_fluid = fields.Boolean(string="Fluid")
    tyre_inspection = fields.Boolean(string="Tyre")
    under_vehicle = fields.Boolean(string="Under Vehicle")
    brake_condition = fields.Boolean(string="Brake Condition")
    vehicle_component = fields.Boolean(string="Multi Point")

    vehicle_inner_body_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                    relation='template_inner_part_rel',
                                                    column1='template_id',
                                                    column2='inner_part_id',
                                                    domain="[('type','=','interior')]")
    vehicle_outer_body_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                    relation='template_outer_part_rel',
                                                    column1='template_id',
                                                    column2='outer_part_id',
                                                    domain="[('type','=','exterior')]")
    vehicle_mechanical_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                    relation='template_under_hood_part_rel',
                                                    column1='template_id',
                                                    column2='under_hood_part_id',
                                                    domain="[('type','=','under_hood')]")
    vehicle_fluid_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                               relation='template_fluid_rel',
                                               column1='template_id',
                                               column2='fluid_part_id',
                                               domain="[('type','=','fluid')]")
    vehicle_tyre_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                              relation='template_tyre_rel',
                                              column1='template_id',
                                              column2='tyre_part_id',
                                              domain="[('type','=','tyre')]")
    vehicle_under_vehicle_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                       relation='template_under_vehicle_rel',
                                                       column1='template_id',
                                                       column2='under_vehicle_part_id',
                                                       domain="[('type','=','under_vehicle')]")
    vehicle_brake_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                               relation='template_brake_rel',
                                               column1='template_id',
                                               column2='brake_part_id',
                                               domain="[('type','=','brake')]")
    vehicle_component_parts_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                   relation='template_component_rel',
                                                   column1='template_id', column2='component_part_iod',
                                                   domain="[('type','=','multi_point')]")

    # DEPRECATED START----------------------------------------------------------------------
    # Template Lines
    vehicle_inner_inspection_ids = fields.One2many('template.vehicle.interior',
                                                   'template_id')

    # Vehicle Body Outer Conditions
    vehicle_outer_inspection_ids = fields.One2many('template.vehicle.outer',
                                                   'template_id')

    # Mechanical Conditions
    vehicle_mechanical_inspection_ids = fields.One2many('template.mechanical.condition',
                                                        'template_id')

    # Vehicle Components
    vehicle_components_inspection_ids = fields.One2many('template.vehicle.components',
                                                        'template_id', string="Multi-Point Inspection")

    # Vehicle Fluids
    vehicle_fluid_inspection_ids = fields.One2many('template.vehicle.fluids',
                                                   'template_id')

    # Tyres Inspections
    vehicle_tyre_inspection_ids = fields.One2many('template.tyre.inspection',
                                                  'template_id')


# Vehicle Body Inner Conditions
class TemplateVehicleInterior(models.Model):
    _name = "template.vehicle.interior"
    _description = "Template Vehicle Interior"
    _rec_name = 'template_id'

    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'interior')]")
    template_id = fields.Many2one('health.report.template')


# Vehicle Body Outer Conditions
class TemplateVehicleOuter(models.Model):
    _name = "template.vehicle.outer"
    _description = "Template Vehicle Outer"
    _rec_name = 'vehicle_view'

    vehicle_view = fields.Selection([('top', "Top View"),
                                     ('bottom', "Bottom View"),
                                     ('left_side', "Left Side View"),
                                     ('right_side', "Right Side View"),
                                     ('front', "Front View"),
                                     ('back', "Back View")],
                                    string="Vehicle View", required=True)
    vehicle_condition_location_id = fields.Many2one('vehicle.condition.location', string="Location", required=True)
    vehicle_condition_id = fields.Many2one('vehicle.condition', string="Condition", required=True)
    condition_code = fields.Char(string="Condition Code")
    template_id = fields.Many2one('health.report.template')

    @api.onchange('vehicle_condition_id')
    def get_condition_description(self):
        for rec in self:
            if rec.vehicle_condition_id:
                rec.condition_code = rec.vehicle_condition_id.condition_code


# Mechanical Conditions
class TemplateMechanicalCondition(models.Model):
    _name = "template.mechanical.condition"
    _description = "Template Mechanical Condition"
    _rec_name = 'vehicle_item_id'

    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'mechanical')]")
    template_id = fields.Many2one('health.report.template')


# Vehicle Components
class TemplateVehicleComponents(models.Model):
    _name = "template.vehicle.components"
    _description = "Multi-Point Inspection"
    _rec_name = 'vehicle_component_id'

    vehicle_component_id = fields.Many2one('vehicle.component', string="Component", required=True)
    template_id = fields.Many2one('health.report.template')


# Vehicle Fluids
class TemplateVehicleFluids(models.Model):
    _name = "template.vehicle.fluids"
    _description = "Template Vehicle Fluids"
    _rec_name = 'vehicle_fluid_id'

    f_vehicle_side = fields.Selection([('top_side', "Top Side"),
                                       ('bottom_side', "Bottom Side")],
                                      string="Vehicle Side", required=True)
    vehicle_fluid_id = fields.Many2one('vehicle.fluid', string="Fluid",
                                       domain="[('fluid_vehicle_side', '=', f_vehicle_side)]", required=True)
    template_id = fields.Many2one('health.report.template')


# Tyres Inspections
class TemplateTyreInspection(models.Model):
    _name = 'template.tyre.inspection'
    _description = "Template Tyre Inspection"
    _rec_name = 'tyre'

    tyre = fields.Selection([('lf', "Left Front"),
                             ('rf', "Right Front"),
                             ('lr', "Left Rear"),
                             ('rr', "Right Rear")],
                            string="Tyre Location", required=True)
    template_id = fields.Many2one('health.report.template')

# DEPRECATED END--------------------------------------------------------------------------------------------------------
