# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _get_targeted_move_ids(self):
        moves = super(StockLandedCost, self)._get_targeted_move_ids()
        moves_to_remove = self.env["stock.move"]
        moves_to_add = self.env["stock.move"]
        for move in moves:
            mo = move.move_orig_ids.production_id[-1:]
            if mo and mo.picking_type_id.code == "mrp_operation":
                moves_to_remove += move
                moves_to_add += move.move_orig_ids
        moves -= moves_to_remove
        moves += moves_to_add
        return moves

    def _compute_allowed_picking_ids(self):
        super(StockLandedCost, self)._compute_allowed_picking_ids()
        valued_picking_ids_per_company = defaultdict(list)
        if self.company_id:
            self.env.cr.execute(
                """
            SELECT sm.picking_id, sm.company_id
            FROM stock_move AS sm
            INNER JOIN stock_move_move_rel AS rel
            ON rel.move_dest_id = sm.id
            INNER JOIN stock_move AS mo_sm
            ON mo_sm.id = rel.move_orig_id
            INNER JOIN mrp_production AS mo
            ON mo.id = mo_sm.production_id
            INNER JOIN stock_picking_type as mo_spt
            ON mo_spt.id = mo.picking_type_id
            INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = mo_sm.id
            WHERE sm.picking_id IS NOT NULL AND sm.company_id IN %s
            AND mo_spt.code='mrp_operation'
            GROUP BY sm.picking_id, sm.company_id""",
                [tuple(self.company_id.ids)],
            )
            for res in self.env.cr.fetchall():
                valued_picking_ids_per_company[res[1]].append(res[0])
        for cost in self:
            picking_ids = valued_picking_ids_per_company[cost.company_id.id]
            if picking_ids:
                additional_pickings = self.env["stock.picking"].browse(picking_ids)
                cost.allowed_picking_ids += additional_pickings
