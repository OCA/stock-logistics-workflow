# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    force_move_type = fields.Boolean(
        string="Force Shipping Policy",
        help=(
            "Force the shipping policy of the operation type "
            "(ignore the one from procurement group)"
        ),
        default=False,
    )
