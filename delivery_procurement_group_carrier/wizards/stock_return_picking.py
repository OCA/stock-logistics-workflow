# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super()._prepare_move_default_values(return_line, new_picking)
        group = new_picking.move_lines.group_id
        if not group:
            group = self.env["procurement.group"].create({"name": new_picking.name})
        vals["group_id"] = group.id
        return vals
