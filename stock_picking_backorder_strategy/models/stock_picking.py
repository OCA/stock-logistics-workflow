# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_backorder(self):
        self.ensure_one()
        # If strategy == 'manual', let the normal process going on
        if self.picking_type_id.backorder_strategy == "manual":
            return super(StockPicking, self)._check_backorder()
        return False

    def _create_backorder(self):
        # Do nothing with pickings 'no_create'
        pickings = self.filtered(
            lambda p: p.picking_type_id.backorder_strategy != "no_create"
        )
        pickings_no_create = self - pickings
        pickings_no_create.mapped("move_lines")._cancel_remaining_quantities()
        res = super(StockPicking, pickings)._create_backorder()
        to_cancel = res.filtered(
            lambda b: b.backorder_id.picking_type_id.backorder_strategy == "cancel"
        )
        to_cancel.action_cancel()
        return res
