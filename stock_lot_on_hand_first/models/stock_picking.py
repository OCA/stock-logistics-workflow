# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    display_lots_on_hand_first = fields.Boolean(
        related="picking_type_id.display_lots_on_hand_first",
    )
