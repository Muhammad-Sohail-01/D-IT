from odoo import api, fields, models, _


# Customer Tags
class CustomerTags(models.Model):
    _name = 'customer.tags'
    _description = "Customer Tags"

    name = fields.Char(string="Title")
    color = fields.Integer(string="Color")


# Concern Type
class ConcernType(models.Model):
    _name = 'concern.type'
    _description = "Consent Types"

    name = fields.Char(string="Title")


# Inspection Configurations
class VehicleItem(models.Model):
    """Vehicle Item"""
    _name = "vehicle.item"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    item_category = fields.Selection([('mechanical', "Mechanical Item"), ('interior', "Interior Item")],
                                     required=True, string="Category")


class VehicleConditionLocation(models.Model):
    """Vehicle Condition Location"""
    _name = "vehicle.condition.location"
    _description = __doc__
    _rec_name = 'location'

    location = fields.Char(string="Location", required=True, translate=True)


class VehicleCondition(models.Model):
    """Vehicle Condition"""
    _name = "vehicle.condition"
    _description = __doc__
    _rec_name = 'condition'

    condition = fields.Char(string="Condition", required=True, translate=True)
    condition_code = fields.Char(string="Condition Code", translate=True)


class VehicleComponent(models.Model):
    """Vehicle Component"""
    _name = "vehicle.component"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    # DEPRECATED
    compo_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")],
                                          string="Vehicle Side")


class VehicleFluid(models.Model):
    """Vehicle Fluid"""
    _name = "vehicle.fluid"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    fluid_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")],
                                          string="Vehicle Side", required=True)


class VehiclePartInfo(models.Model):
    """Vehicle Part Info"""
    _name = 'vehicle.part.info'
    _description = "Vehicle Part Info"

    name = fields.Char(string="Title")
    type = fields.Selection(selection=[('interior', 'Interior'),
                                       ('exterior', 'Exterior'),
                                       ('under_hood', 'Under Hood'),
                                       ('fluid', 'Fluid'),
                                       ('tyre', 'Tyre'),
                                       ('under_vehicle', 'Under Vehicle'),
                                       ('brake', 'Brake'),
                                       ('multi_point', 'Multi Point')],
                            string="Type")


class InspectionType(models.Model):
    _name = 'inspection.type'
    _description = 'Inspection Type'

    name = fields.Char(string="Title")
    hours = fields.Float(string="Hours")


class VehicleTermsConditions(models.Model):
    _name = 'vehicle.terms.conditions'
    _description = 'Vehicle Terms Conditions'

    name = fields.Char(string="Title")
    terms_conditions = fields.Html(string="Terms & Conditions")


# Vehicle Quality Checks Template
class VehicleQCTemplate(models.Model):
    _name = 'vehicle.qc.template'
    _description = "Vehicle QC Template"

    name = fields.Char(string="Title")
    template_line_ids = fields.One2many(comodel_name='vehicle.qc.template.line', inverse_name='template_id')


class VehicleQCTemplateLine(models.Model):
    _name = 'vehicle.qc.template.line'
    _description = "Vehicle QC Template Line"

    name = fields.Char(string="Checkpoint")
    template_id = fields.Many2one(comodel_name='vehicle.qc.template')
    sequence = fields.Integer()
    display_type = fields.Selection(selection=[('line_section', "Section"),
                                               ('line_note', "Note")], default=False)


# Vehicle Job Card Photos Template
class JobImageTemplate(models.Model):
    _name = 'job.image.template'
    _description = "Job Card Image Template"

    name = fields.Char(string="Title")
    inner_body_image_ids = fields.Many2many(comodel_name='job.image.template.line',
                                            relation='inner_body_template_rel',
                                            column1='inner_body_image_id',
                                            column2='inner_body_template_id',
                                            string="Inner Body Images")
    outer_body_image_ids = fields.Many2many(comodel_name='job.image.template.line',
                                            relation='outer_body_template_rel',
                                            column1='outer_body_image_id',
                                            column2='outer_body_template_id',
                                            string="Outer Body Images")
    other_image_ids = fields.Many2many(comodel_name='job.image.template.line',
                                       relation='other_image_template_rel',
                                       column1='other_image_id',
                                       column2='other_image_template_id',
                                       string="Other Images")


class JobImageTemplateLine(models.Model):
    _name = 'job.image.template.line'
    _description = "Job Card Image Template"

    name = fields.Char(string="Title")


# DEPRECATED MODELS
# Concern Template
class VehicleConcernTemplate(models.Model):
    _name = 'vehicle.concern.template'
    _description = "Vehicle Consent Template"

    name = fields.Char(string="Title")
    concern = fields.Html(string="Consent")
