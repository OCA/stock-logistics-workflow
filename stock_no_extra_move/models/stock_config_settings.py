# -*- coding: utf-8 -*-
# Copyright 2018 Julien Coux (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    percent_increase_quantity_allowed = fields.Float(
        string='Allowed percent of increase quantity for transfer',
        default=10.,
    )

    @api.model
    def get_default_percent_increase_quantity_allowed(self, fields=False):
        res = {}
        icp = self.env['ir.config_parameter']
        res['percent_increase_quantity_allowed'] = float(icp.get_param(
            'percent_increase_quantity_allowed',
            10.
        ))
        return res

    @api.multi
    def set_percent_increase_quantity_allowed(self):
        if self.percent_increase_quantity_allowed:
            icp = self.env['ir.config_parameter']
            icp.set_param('percent_increase_quantity_allowed',
                          self.percent_increase_quantity_allowed)
