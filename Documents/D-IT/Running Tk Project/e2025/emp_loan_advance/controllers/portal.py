from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request


class LoanPortal (CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super ()._prepare_home_portal_values (counters)
        if 'loan_count' in counters:
            loan_count = request.env['hr.loan'].search_count ([
                ('employee_id.user_id', '=', request.env.user.id)
            ])
            values['loan_count'] = loan_count
        return values

    @http.route (['/my/loans', '/my/loans/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loans(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values ()
        Loan = request.env['hr.loan']

        domain = [
            ('employee_id.user_id', '=', request.env.user.id)
        ]

        searchbar_sortings = {
            'date': {'label': _ ('Request Date'), 'order': 'date_request desc'},
            'name': {'label': _ ('Reference'), 'order': 'name'},
            'state': {'label': _ ('Status'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Count for pager
        loan_count = Loan.search_count (domain)

        # Pager
        pager = portal_pager (
            url="/my/loans",
            url_args={'sortby': sortby},
            total=loan_count,
            page=page,
            step=self._items_per_page
        )

        # Content according to pager and archive selected
        loans = Loan.search (
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update ({
            'loans': loans,
            'page_name': 'loan',
            'pager': pager,
            'default_url': '/my/loans',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render ("hr_loan.portal_my_loans", values)

    @http.route (['/my/loans/<int:loan_id>'], type='http', auth="user", website=True)
    def portal_my_loan(self, loan_id=None, **kw):
        loan = request.env['hr.loan'].sudo ().browse (loan_id)
        if not loan.exists () or loan.employee_id.user_id != request.env.user:
            return request.redirect ('/my')

        values = {
            'page_name': 'loan',
            'loan': loan,
        }
        return request.render ("hr_loan.portal_my_loan", values)