# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"
    _order = "priority desc, id"

    priority = fields.Selection(
        selection=[
            ("0", "Normal"),
            ("1", "Important"),
        ],
        default="0",
        copy=False,
    )
