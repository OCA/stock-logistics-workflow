# Copyright 2023 Raumschmiede Gmbh
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    automatic_package_creation_mode = fields.Selection(
        [("single", "Single Package"), ("packaging", "Per Smallest Packaging")],
        help="Automatically create the delivery packages. Any lines not in "
        "a package will automaticaly be packaged.",
    )
