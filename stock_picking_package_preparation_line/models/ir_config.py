# -*- coding: utf-8 -*-
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
#    Copyright 2015 Lorenzo Battistini - Agile Business Group
#    Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockConfigSettings(models.TransientModel):

    _inherit = 'stock.config.settings'

    default_picking_type_for_package_preparation_id = fields.Many2one(
        'stock.picking.type',
        related='company_id.default_picking_type_for_package_preparation_id')

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)
        if res:
            company = self.env.user.company_id
            res['default_picking_type_for_package_preparation_id'] = \
                company.default_picking_type_for_package_preparation_id.id \
                if company.default_picking_type_for_package_preparation_id \
                else False
        return res
