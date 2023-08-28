# -*- coding: utf-8 -*-

from odoo import models, fields


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    team_ids = fields.Many2many('crm.team',string='Branchs')

