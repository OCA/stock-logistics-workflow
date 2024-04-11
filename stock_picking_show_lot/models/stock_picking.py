# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_show_lots(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_production_lot_form"
        )
        if len(self.move_line_ids.lot_id.ids) == 1:
            action["views"] = [
                (view, mode) for view, mode in action["views"] if mode == "form"
            ]
            action["res_id"] = self.move_line_ids.lot_id.id
            action["view_mode"] = "form"
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", self.move_line_ids.lot_id.ids)]
        action["context"] = {}
        action["name"] = _("Lots")
        return action
