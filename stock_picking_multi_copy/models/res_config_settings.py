# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deliveryslip_folder = fields.Char(
        string='Delivery Slip Folder',
        help='Directory where to store Delivery Slip report',)

    @api.model
    def get_values(self):
        param_obj = self.env['ir.config_parameter']
        res = super(ResConfigSettings, self).get_values()
        res.update(
            deliveryslip_folder=param_obj.sudo().get_param(
                'stock_picking_multi_copy.'
                'field_res_config_settings__deliveryslip_folder'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        deliveryslip_folder = self.deliveryslip_folder or False

        param.set_param(
            'stock_picking_multi_copy.'
            'field_res_config_settings__deliveryslip_folder',
            deliveryslip_folder
        )
