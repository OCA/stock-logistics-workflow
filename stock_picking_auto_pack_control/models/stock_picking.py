# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _auto_create_delivery_package_filter(self, move_lines):
        move_lines = super()._auto_create_delivery_package_filter(move_lines)
        move_lines = move_lines.filtered(
            lambda ml: ml.product_id.uom_ids
            or not ml.picking_type_id.auto_pack_requires_packaging
        )
        return move_lines
