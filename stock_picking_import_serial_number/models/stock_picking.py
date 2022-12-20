# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    import_lot_from_file = fields.Boolean(
        compute="_compute_import_lot_from_file", store=True, readonly=False
    )

    @api.depends("use_create_lots")
    def _compute_import_lot_from_file(self):
        for rec in self:
            if rec.use_create_lots:
                rec.import_lot_from_file = True
            else:
                rec.import_lot_from_file = False


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # To use in picking view to display import button
    import_lot_from_file = fields.Boolean(
        related="picking_type_id.import_lot_from_file"
    )
