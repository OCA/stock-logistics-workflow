# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WeightMixin(models.AbstractModel):
    _name = "weighing.mixin"
    _description = "To be used by stock.move and stock.move.line"

    has_weight = fields.Boolean(
        compute="_compute_has_weight", search="_search_has_weight"
    )

    @api.depends("product_uom_category_id")
    def _compute_has_weight(self):
        """Product UOM is a weighed one"""
        self.has_weight = False
        self.filtered(
            lambda x: x.product_uom_category_id
            == self.env.ref("uom.product_uom_categ_kgm")
        ).has_weight = True

    def _search_has_weight(self, operator, value):
        return [
            (
                "product_uom_category_id",
                operator,
                self.env.ref("uom.product_uom_categ_kgm").id,
            )
        ]
