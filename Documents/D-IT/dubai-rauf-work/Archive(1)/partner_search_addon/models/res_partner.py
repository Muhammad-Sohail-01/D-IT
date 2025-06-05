from odoo import api, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100,
                     order=None):
        args = args or []
        domain = ['|', '|', '|', ('name', operator, name),
                  ('phone', operator, name), ('email', operator, name),
                  ('mobile', operator, name)]
        return self._search(expression.AND([domain + args]), limit=limit, order=order)
