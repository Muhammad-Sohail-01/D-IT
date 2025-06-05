# __manifest__.py
{
    'name': 'Cost Allocation',
    'version': '1.0',
    "license": "OPL-1",
    'depends': ['account_accountant', 'account','tk_vehicle_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_cost.xml',
        # 'views/inv_inv_tag.xml',
    ],
    'installable': True,
    'application': False,
}
