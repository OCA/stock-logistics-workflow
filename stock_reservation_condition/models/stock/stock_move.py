# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_assign(self, no_prepare=False):
        for move in self.sorted(key=lambda m: m.picking_id.min_date):
            if move.picking_type_id.code != 'outgoing':
                super(StockMove, move).action_assign(no_prepare=no_prepare)
                continue

            order = self.env['sale.order'].search([
                ('procurement_group_id', '=', move.group_id.id),
                ('state', 'in', ['sale', 'done'])
            ])
            order.ensure_one()
            if order:
                if not order.reservation_date \
                   and len(order.reservation_po_ids) == 0:
                    skip_reservation = False
                elif order.reservation_po_ids:
                    skip_reservation = False
                    for purchase in order.reservation_po_ids:
                        picking_ids = purchase.picking_ids.filtered(
                            lambda p: p.min_date > fields.Datetime.now())
                        if move.product_id in picking_ids.mapped(
                           'move_lines').mapped('product_id'):
                            skip_reservation = True

                elif order.reservation_date < fields.Date.today():
                    skip_reservation = False
                else:
                    skip_reservation = True

                if skip_reservation:
                    continue
                else:
                    super(StockMove, move).action_assign(no_prepare=no_prepare)
