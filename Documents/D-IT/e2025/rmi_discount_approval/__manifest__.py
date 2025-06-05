
{
    'name': 'Product Discount Limit',
    'version': '17.0.1.0.1',
    'category': 'Sales',
    'summary': 'Product Discount Limit',
    'description': 'This module allows setting discount limits for each product.',
    'author': 'Rauff M Imasdeen',
    'email': 'rauffmimas@gmail.com',
    'mobile': '+971582878939',
    'depends': ['sale', 'purchase', 'stock', 'tk_vehicle_management'],
    'data': [

        'data/mail_activity_type_data.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/sale_order_line.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/sale_order_view.xml',
        'views/job_card_part_inherit.xml',
        'views/job_card_service_inherit.xml',
        
        
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
