# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_change_move_dest_qty(self):
        action = self.env[
            "stock.reception.discrepancy.distribution.wiz"
        ].get_formview_action()
        action["context"]["default_move_id"] = self.id
        action["target"] = "new"
        view = (
            "stock_reception_discrepancy_distribution."
            "stock_reception_discrepancy_distribution_wiz"
        )
        action["views"] = [
            (
                self.env.ref(view).id,
                "form",
            )
        ]
        return action
