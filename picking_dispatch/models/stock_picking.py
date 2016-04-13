# -*- coding: utf-8 -*-
# @2016 Cyril Gaudin, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    related_dispatch_ids = fields.One2many(
        comodel_name='picking.dispatch',
        compute='_get_related_dispatch',
        search='_search_dispatch_pickings',
        string='Related Dispatch Picking'
    )

    @api.multi
    def _get_related_dispatch(self):
        if not self.ids:
            return

        sql = ("SELECT sm.picking_id, array_agg(sm.dispatch_id) "
               "FROM stock_move sm "
               "WHERE sm.picking_id in %s AND sm.dispatch_id is NOT NULL "
               "GROUP BY sm.picking_id")
        self.env.cr.execute(sql, (tuple(self.ids),))

        picking_distpatches = {
            row[0]: row[1] for row in self.env.cr.fetchall()
        }

        for picking in self:
            picking.related_dispatch_ids = picking_distpatches[picking.id]

    @api.multi
    def _search_dispatch_pickings(self, operator, value):
        moves = self.env['stock.move'].search(
            [('dispatch_id', operator, value)]
        )

        picking_ids = {move.picking_id.id for move in moves}
        return [('id', 'in', list(picking_ids))]
