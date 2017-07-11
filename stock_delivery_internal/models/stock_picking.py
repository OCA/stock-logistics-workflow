# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def action_confirm(self):
        for rec in self.filtered(
                lambda s: s.carrier_id.delivery_type == 'internal'):
            self.env['stock.pickup.request'].create({
                'picking_id': rec.id,
                'company_id':
                    rec.carrier_id.internal_delivery_company_id.id,
            })
        return super(StockPicking, self).action_confirm()
