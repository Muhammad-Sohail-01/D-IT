# -*- coding: utf-8 -*-
from . import models
from . import wizard

# TODO: Apply proper fix & remove in master


def post_init_hook(env):
    # Update old customers and vendors.
    account_obj = env['account.account']
    for company in env['res.company'].sudo().search([]):
        company.write({
            'pdc_customer': account_obj.search([('name','=','PDC Receivable'),('company_id','=',company.id)],limit=1).id,
            'pdc_vendor':account_obj.search([('name','=','PDC Payable'),('company_id','=',company.id)],limit=1).id
        })
