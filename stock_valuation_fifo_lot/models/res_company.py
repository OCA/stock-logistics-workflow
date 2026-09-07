# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_lot_cost_for_new_stock = fields.Boolean(
        "Use Last Lot/Serial Cost for New Stock",
        default=True,
        help="Use the lot/serial cost for FIFO products for non-purchase receipts.",
    )
