# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_moves_to_unreserve(
        self,
        location,
        product=None,
        picking_types=None,
        location_operator="child_of",
        picking_type_operator="in",
        extra_domain=None,
    ):
        """Return the moves to unreserve corresponding to different critera.

        NOTE: `extra_domain` parameter is applied on `stock.move.line` data model.
        """
        if extra_domain is None:
            extra_domain = []
        domain = [
            ("location_id", location_operator, location.id),
            ("state", "in", ("assigned", "partially_available")),
            ("qty_done", "=", 0),
        ]
        if product:
            domain.append(("product_id", "=", product.id))
        if picking_types:
            domain.append(
                ("move_id.picking_type_id", picking_type_operator, picking_types.ids)
            )
        if extra_domain:
            domain = expression.AND([domain, extra_domain])
        all_lines = self.env["stock.move.line"].search(domain)
        return all_lines.move_id
