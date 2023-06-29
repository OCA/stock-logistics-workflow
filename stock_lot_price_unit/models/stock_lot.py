# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    # We make this field editable on purpose so that the user can change the price as
    # appropriate.
    price_unit = fields.Float(
        "Reference Price",
        help="The value represents the unit price of the stock move that has created "
        "this lot. The value is for reference only, and may not be accurate.",
        tracking=True,
    )
