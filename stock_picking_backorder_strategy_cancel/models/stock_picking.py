# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_backorder(self, backorder_moves=None):
        res = super()._create_backorder(backorder_moves=backorder_moves)
        to_cancel = res.filtered(
            lambda b: b.picking_type_id.create_backorder == "cancel"
        )
        to_cancel.action_cancel()
        return res
