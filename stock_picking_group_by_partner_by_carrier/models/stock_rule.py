# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        # We propagate the original_group_id on pull moves to allow to prevent
        # merging pulled moves. This allows to cancel a SO without canceling
        # pulled moves from other SO (as we ensure they are not merged).
        move_values["original_group_id"] = (
            values.get("move_dest_ids", self.env["stock.move"]).original_group_id.id
            or move_values["group_id"]
        )
        return move_values
