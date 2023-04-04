# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_create_lot = fields.Boolean()
    auto_create_lot_name_expression = fields.Char(
        "Lot Name Expression",
        help="Expression to use for auto-created lot names; leave empty to "
        "use the default name",
    )
    auto_create_lot_for_all_products = fields.Boolean(
        "Auto Create Lots for All Products",
        help="Auto-create lots for all products, ignoring their Auto Create "
        "Lot property",
    )
