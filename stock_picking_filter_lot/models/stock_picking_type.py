# Copyright 2021 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_filter_lots = fields.Boolean(
        "Use only available lots",
        default=True,
        help="If this is checked, only lots available in source location \
            would be displayed in drop down list for selecting lot.",
    )
