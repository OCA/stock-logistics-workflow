# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_cancel_with_orig_move = fields.Boolean(
        string="Restrict Cancellation with Original Moves",
        help="If enabled, cancellation of a picking is blocked when any of its "
        "moves has a previous move that is not yet cancelled or done.",
    )
