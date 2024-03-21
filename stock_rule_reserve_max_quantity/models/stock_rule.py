# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    reserve_max_quantity = fields.Boolean(
        help="If checked, the system will reserve the maximum quantity "
        "available for the moves that have this rule linked, when the quantity "
        "available exceeds the quantity demanded",
        default=False,
    )
