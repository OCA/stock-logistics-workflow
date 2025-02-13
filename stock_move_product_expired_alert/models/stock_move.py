# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_moves_per_picking_for_expiry_alert(self):
        """
        Gather product moves that have expired products
        grouped per picking
        """
        for picking, moves in (
            self.filtered(
                lambda move: any(
                    line.has_expired_product for line in move.move_line_ids
                )
            )
            .partition("picking_id")
            .items()
        ):
            yield picking, moves

    def _get_expiry_alert_message(self):
        note = ""
        for line in self.move_line_ids.filtered(lambda line: line.has_expired_product):
            # Building the alert message
            note += _(
                "\n - Product: %(product_name)s (Lot: %(lot_name)s)",
                product_name=line.product_id.display_name,
                lot_name=line.lot_id.display_name,
            )
        return note

    def _check_expired_product_move_alert(self):
        """
        This will check if the product that goes into stock is expired.

        If it is the case, create an activity for users in the
        configured team.
        """
        # Group expired moves per picking to limit the amount of activities
        for picking, moves in self._get_moves_per_picking_for_expiry_alert():
            summary = _(
                "Expired products transferred in %(picking_name)s",
                picking_name=picking.display_name,
            )
            act_values = {}
            team = picking.company_id.check_expired_product_alert_team_id
            if team:
                act_values.update({"team_id": team.id})
            picking.activity_schedule(
                "stock_move_product_expired_alert.expired_product_alert",
                date_deadline=None,
                summary=summary,
                note=moves._get_expiry_alert_message(),
                **act_values,
            )

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        # Do it after super() call as the lot can have been created there.
        self._check_expired_product_move_alert()
        return res
