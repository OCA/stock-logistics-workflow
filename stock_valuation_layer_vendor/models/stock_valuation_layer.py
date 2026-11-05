# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    vendor_id = fields.Many2one(
        "res.partner",
        readonly=True,
        index=True,
        help="Vendor of the purchase order linked to the stock move, if any.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        move_ids = [
            vals["stock_move_id"] for vals in vals_list if vals.get("stock_move_id")
        ]
        # Resolve the vendor per move once, letting the ORM prefetch the
        # related purchase order and partner in batch.
        moves = self.env["stock.move"].browse(move_ids)
        vendor_by_move = {
            move.id: move.purchase_line_id.partner_id.id
            for move in moves
            if move.purchase_line_id
        }
        for vals in vals_list:
            vendor_id = vendor_by_move.get(vals.get("stock_move_id"))
            if vendor_id:
                vals["vendor_id"] = vendor_id
        return super().create(vals_list)
