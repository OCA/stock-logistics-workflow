# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    @api.model
    def _default_shipping_policy(self):
        return "procurement_group"

    @api.model
    def _selection_shipping_policy(self):
        return [
            ("procurement_group", "Take from procurement group"),
            ("force_as_soon_as_possible", "Force to as soon as possible"),
            ("force_all_products_ready", "Force to when all products are ready"),
        ]

    shipping_policy = fields.Selection(
        selection="_selection_shipping_policy",
        default=lambda r: r._default_shipping_policy(),
        help="Allows to force the shipping policy on pickings according to the"
        " picking type.",
    )
