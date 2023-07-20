# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        self = self.with_context(self._set_context(options)) # For multicompany, when allowed companies are changed by options (such as aggregare_tax_unit)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        # Inherit
        if options.get('analytic_account_groups') is not None:
            options['selected_analytic_groups'] = [self.env['account.analytic.group'].browse(int(group)).name for group in options['analytic_account_groups']]
        # 
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]
            

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info    

    @api.model
    def _init_filter_analytic(self, options, previous_options=None):
        if not self.filter_analytic:
            return

        enable_analytic_accounts = self.user_has_groups('analytic.group_analytic_accounting')
        enable_analytic_tags = self.user_has_groups('analytic.group_analytic_tags')
        if not enable_analytic_accounts and not enable_analytic_tags:
            return

        if enable_analytic_accounts:
            previous_analytic_accounts = (previous_options or {}).get('analytic_accounts', [])
            analytic_account_ids = [int(x) for x in previous_analytic_accounts]
            selected_analytic_accounts = self.env['account.analytic.account'].search([('id', 'in', analytic_account_ids)])
            options['analytic_accounts'] = selected_analytic_accounts.ids
            options['selected_analytic_account_names'] = selected_analytic_accounts.mapped('name')

            # Inherit
            previous_analytic_groups = (previous_options or {}).get('analytic_account_groups', [])
            analytic_group_ids = [int(x) for x in previous_analytic_groups]
            selected_analytic_groups = self.env['account.analytic.group'].search([('id', 'in', analytic_group_ids)])
            options['analytic_account_groups'] = selected_analytic_groups.ids
            options['selected_analytic_groups'] = selected_analytic_groups.mapped('name')
            # 

        if enable_analytic_tags:
            previous_analytic_tags = (previous_options or {}).get('analytic_tags', [])
            analytic_tag_ids = [int(x) for x in previous_analytic_tags]
            selected_analytic_tags = self.env['account.analytic.tag'].search([('id', 'in', analytic_tag_ids)])
            options['analytic_tags'] = selected_analytic_tags.ids
            options['selected_analytic_tag_names'] = selected_analytic_tags.mapped('name')


    @api.model
    def _get_options_analytic_domain(self, options):
        domain = super(AccountReport, self)._get_options_analytic_domain(options)

        # Inherit
        if options.get('analytic_account_groups'):
            analytic_group_ids = [int(acc) for acc in options['analytic_account_groups']]
            domain.append(('analytic_account_id.group_id', 'in', analytic_group_ids))
        # 
        return domain
