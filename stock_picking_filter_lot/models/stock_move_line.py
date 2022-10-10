# Copyright 2021 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_use_filter_lots = fields.Boolean(
        related="picking_id.picking_type_id.use_filter_lots"
    )
