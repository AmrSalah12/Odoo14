# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('pricelist_id')
    def onchange_pricelist(self):
        team_id = (self.env['crm.team'].search([('member_ids', 'in', self.env.user.id)]))

        for order in self:
            if order.pricelist_id\
                and order.pricelist_id.team_ids\
                and team_id not in order.pricelist_id.team_ids:
                raise ValidationError(
                    'This pricelist is not availabe for this branch.')

