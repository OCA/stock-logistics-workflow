# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    reservation_date = fields.Date(
        "Date to Reserve",
        compute="_compute_reservation_date",
        store=True,
        help="This is a technical field for calculating when a move should be reserved",
    )

    @api.depends("picking_type_id", "date_expected")
    def _compute_reservation_date(self):
        for move in self:
            if move.picking_type_id.reservation_method == "by_date" and move.state in [
                "draft",
                "confirmed",
                "waiting",
                "partially_available",
            ]:
                days = move.picking_type_id.reservation_days_before
                move.reservation_date = fields.Date.to_date(
                    move.date_expected
                ) - timedelta(days=days)
            else:
                move.reservation_date = fields.Date.to_date(move.date_expected)
