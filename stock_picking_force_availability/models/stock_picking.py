# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_force_availability(self):
        self.ensure_one()
        # Try to reserve the goods before inviting the user to unreserve others
        self.action_assign()
        if not self.show_check_availability:
            return True
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_force_availability.stock_picking_force_availability_action"
        )
        action.update(
            {
                "active_id": self.id,
                "active_model": self._name,
            }
        )
        return action
