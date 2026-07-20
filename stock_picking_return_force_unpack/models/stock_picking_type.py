# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    force_unpack_on_return = fields.Boolean(
        string="Force Unpack on Return",
        default=False,
        help=(
            "When a return or exchange is created with this operation type, "
            "strip the destination package assignment from its stock moves "
            "so the returned quantity is received unpackaged instead of "
            "recreating the original container. The source package is kept "
            "so the move still resolves against the correct quant "
            "(important for lot/serial tracking); prevents a partial "
            "return from being stuck in a package that is still partly "
            "held at the customer."
        ),
    )
