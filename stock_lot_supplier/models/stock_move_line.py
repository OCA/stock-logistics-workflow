# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super()._action_done()
        incoming_lines = self.exists().filtered(
            lambda ml: ml.picking_id.picking_type_code == "incoming"
            and ml.lot_id
            and not ml.lot_id.supplier_id
            and ml.picking_id.partner_id
        )
        for ml in incoming_lines:
            ml.lot_id.supplier_id = ml.picking_id.partner_id
        return res
