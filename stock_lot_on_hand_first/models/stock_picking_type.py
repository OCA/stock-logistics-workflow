# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    display_lots_on_hand_first = fields.Boolean(
        compute="_compute_display_lots_on_hand_first",
        store=True,
        readonly=False,
        help="When marked, lots that do not have a quantity in stock will be displayed"
        " last in the selection",
    )

    @api.depends("use_existing_lots")
    def _compute_display_lots_on_hand_first(self):
        """Reset display_lots_on_hand_first if use_existing_lots is set to False"""
        for picking_type in self:
            if not picking_type.use_existing_lots:
                picking_type.display_lots_on_hand_first = False
