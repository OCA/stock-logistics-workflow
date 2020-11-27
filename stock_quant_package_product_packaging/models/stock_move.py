# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        # In odoo 13, action_done on stock move call an action_done method
        # on stock.move.line (new name for stock.pack.operation)
        # To keep the same approach as the one defined into the V13 version of
        # this addon, the auto assignment of product.packaging on the
        # stock.quant.package is triggered on the stock.pack.operation when
        # the move is done.
        res = super(StockMove, self).action_done()
        operations = self.filtered(lambda move: move.state == "done").mapped(
            "linked_move_operation_ids.operation_id"
        )
        operations.auto_assign_packaging()
        return res
