# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_fill_operation = fields.Boolean(
        string="Auto fill operations",
        help="To auto fill done quantity in picking document.\n"
        "- If checked, auto fill done quantity automatically\n"
        "- If unchecked, show button AutoFill"
        " for user to do the auto fill manually",
    )
    avoid_lot_assignment = fields.Boolean(
        string="Avoid auto-assignment of lots",
        help="Avoid auto fill for more line with lots product",
        default=True,
    )
