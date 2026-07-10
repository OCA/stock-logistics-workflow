# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_partial_validation = fields.Boolean(
        help="Transfers of this operation type can only be validated when "
        "they are fully reserved and processed in full: validation is "
        "blocked while the transfer is not in Ready state, and when any "
        "line is processed for less than the demanded quantity, so no "
        "backorder can be created.",
    )
