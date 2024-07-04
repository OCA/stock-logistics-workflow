# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.picking"

    original_scheduled_date = fields.Datetime(
        compute="_compute_original_scheduled_date",
        store=True,
        readonly=True,
        tracking=True,
        help="Original Scheduled date for the first part of the "
        "shipment to be processed at transfer confirmation.",
    )

    @api.depends("move_lines.state", "move_lines.original_date", "move_type")
    def _compute_original_scheduled_date(self):
        for picking in self:
            raw_moves_dates = picking.move_lines.filtered(
                lambda move: move.state != "cancel"
            ).mapped("original_date")
            moves_dates = []
            for md in raw_moves_dates:
                if md:
                    moves_dates.append(md)
            if picking.move_type == "direct":
                picking.original_scheduled_date = moves_dates and min(moves_dates)
            else:
                picking.original_scheduled_date = moves_dates and max(moves_dates)
