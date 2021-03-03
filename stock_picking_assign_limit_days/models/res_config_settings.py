# -*- coding: utf-8 -*-
# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_picking_assign_limit_days = fields.Integer(
        string='Stock Picking Assign Limit Days',
        help="A stock move will not be assigned until its date_expected"
        " will be set before to today plus the indicated number of days")

    @api.model
    def get_values(self):
        param_obj = self.env['ir.config_parameter']
        res = super(ResConfigSettings, self).get_values()
        res.update(
            stock_picking_assign_limit_days=param_obj.sudo().get_param(
                'stock_picking_assign_limit_days.'
                'stock_picking_assign_limit_days')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        stock_picking_confirm_before_days =\
            self.stock_picking_confirm_before_days or False

        param.set_param('stock_picking_assign_limit_days.'
                        'stock_picking_assign_limit_days',
                        stock_picking_confirm_before_days)
