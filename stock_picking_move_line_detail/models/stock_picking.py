# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.models import Model


class StockPicking(Model):
    _inherit = "stock.picking"

    def action_picking_move_line_tree(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_picking_move_line_detail.stock_move_line_action"
        )
        action["context"] = self.env.context
        action["domain"] = [("picking_id", "in", self.ids)]
        return action
