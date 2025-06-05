# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Car Garage',
    'version' : '17.0.0.2',
    'sequence': 5,
    'category': 'Garage',
    'website' : '',
    'summary' : 'Manage car garage',
    'description' : """
Vehicle, leasing, insurances, cost, Repairing
==================================
With this module you managing all your Car garage, the
contracts associated to those vehicle as well as services, costs, Repairing
and many other features necessary to the management of your garage
of car(s)

Main Features
-------------
* Add Car brand
* Manage contracts for vehicles
* Reminder when a contract reach its expiration date
* Add services, Repairing cost, values for all vehicles
* Show all costs associated to a vehicle or to a type of service
* Analysis graph for costs
""",
    'depends': [
        'base',
        'mail',
        'sale',
    ],
    'data': [
        'security/car_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/car_brand_views.xml',
        'views/car_history_views.xml',
        'views/res_partner_views.xml',
        'views/car_service_views.xml',
        'views/car_cylinder_view.xml',
        'views/car_spec_view.xml',
        'views/car_gear_box_view.xml',
        'views/car_garage_reference_view.xml',
        'views/car_color_view.xml',
        'views/car_gear_type_view.xml'
    ],

    'installable': True,
    'application': False,
}
