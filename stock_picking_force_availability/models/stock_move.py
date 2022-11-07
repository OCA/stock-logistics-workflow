# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_moves_to_unreserve(
        self,
        location,
        product=None,
        picking_type=None,
        location_operator="child_of",
        exclude_moves=None,
    ):
        """Return the moves to unreserve corresponding to different critera."""
        domain = [
            ("location_id", location_operator, location.id),
            ("state", "in", ("assigned", "partially_available")),
            ("qty_done", "=", 0),
        ]
        if product:
            domain.append(("product_id", "=", product.id))
        if picking_type:
            domain.append(("move_id.picking_type_id", "=", picking_type.id))
        all_lines = self.env["stock.move.line"].search(domain)
        if exclude_moves:
            all_lines -= exclude_moves.move_line_ids
        return all_lines.move_id
