# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime, timedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def purchase_backorder(self):
        procurement_obj = self.env['procurement.order']

        self.ensure_one()
        if not self.picking_type_id.code == 'incoming'\
                or not self.partner_id.purchase_on_no_backorder:
            return False

        backorder_pick = self.search([
            ('backorder_id', '=', self.id)])
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
                            'company_id': backorder_pick.company_id.id,
                            'route_ids': [(6, 0, move.route_ids.ids)],
                        })
            # Cancel backorder:
            if backorder_pick.state != 'cancel':
                backorder_pick.action_cancel()
                self.message_post(
                    body=_("Back order <em>%s</em> <b>cancelled</b>.") %
                    (backorder_pick.name))
        return True
