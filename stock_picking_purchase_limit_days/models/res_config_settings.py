# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_limit_days = fields.Char(
        string='Purchase Limit Days',
        help='Limit Days forward to check whether or not is necessary to buy requiered stock',)

    @api.model
    def get_values(self):
        param_obj = self.env['ir.config_parameter']
        res = super(ResConfigSettings, self).get_values()
        res.update(
            deliveryslip_folder=param_obj.sudo().get_param(
                'stock_picking_purchase_limit_days.'
                'field_res_config_settings__purchase_limit_days'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        purchase_limit_days = self.purchase_limit_days or False

        param.set_param(
            'stock_picking_purchase_limit_days.'
            'field_res_config_settings__purchase_limit_days',
            purchase_limit_days
        )
