# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_manual_lots = fields.Boolean(
        string="Manual Production Lot Selection",
        help="If checked, the user will be able to manually select a production lot "
        "for each move line.",
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    use_manual_lots = fields.Boolean(
        related="picking_type_id.use_manual_lots",
    )
