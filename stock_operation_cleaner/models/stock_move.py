# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def action_cancel(self):
        moves_to_cancel = self.filtered(
            lambda m: m.state not in ("cancel", "done")
        )
        moves_to_cancel._delete_pack_ops()
        return super(StockMove, self).action_cancel()

    @api.multi
    def _delete_pack_ops(self):
        pack_ops_links = self.env["stock.move.operation.link"].search(
            [("move_id", "in", self.ids)]
        )
        pack_ops_links.mapped("operation_id").filtered(
            lambda op: op.qty_done == 0).unlink()
