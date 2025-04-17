# Copyright 2024 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def create_returns(self):
        res = super().create_returns()
        new_picking_id = res.get("res_id")
        if self.picking_id.picking_type_id.empty_package_at_return:
            move_lines = self.env["stock.move.line"].search(
                [("picking_id", "=", new_picking_id)]
            )
            move_lines.result_package_id = False
        return res
