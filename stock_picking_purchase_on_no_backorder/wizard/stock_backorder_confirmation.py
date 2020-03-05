# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.one
    def _process(self, cancel_backorder=False):
        procurement_obj = self.env['procurement.order']

        res = super(StockBackorderConfirmation, self)._process(
            cancel_backorder)
        if cancel_backorder\
                and self.pick_id.picking_type_id.code == 'incoming'\
                and self.pick_id.partner_id.purchase_on_no_backorder:
            # convert cancelled backorder picking into a purchase order:
            backorder_pick = self.env['stock.picking'].search([
                ('backorder_id', '=', self.pick_id.id)])
            if backorder_pick:
                for move in backorder_pick.move_lines:
                    # get move_dest_id:
                    if move.purchase_line_id:
                        procurements = procurement_obj.search([
                            ('purchase_line_id', '=', move.purchase_line_id.id)
                        ])
                        if procurements:
                            procurements[0].copy(default={
                                'product_qty': move.product_qty,
                            })
                        else:
                            now = datetime.now()
                            now_str = now.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT)
                            date = fields.Datetime.from_string(now_str)
                            date = date + timedelta(hours=12)
                            date = fields.Datetime.to_string(date)
                            procurement_obj.create({
                                'name': 'PARTIAL RECEIVED: %s' % (
                                    backorder_pick.name),
                                'date_planned': date,
                                'product_id': move.product_id.id,
                                'product_qty': move.product_qty,
                                'product_uom': move.product_uom.id,
                                'warehouse_id': move.warehouse_id.id,
                                'location_id':
                                    move.warehouse_id.lot_stock_id.id,
                                'company_id': self.pick_id.company_id.id,
                                'route_ids': [(6, 0, move.route_ids.ids)],
                            })
        return res
