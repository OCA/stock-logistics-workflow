# Copyright 2021 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_use_filter_lots = fields.Boolean(
        related="picking_id.picking_type_id.use_filter_lots"
    )
    lot_id_domain = fields.Char(compute="_compute_lot_id_domain")

    @api.depends("picking_type_use_filter_lots")
    def _compute_lot_id_domain(self):
        for rec in self:
            default_domain = (
                ("product_id", "=", rec.product_id.id),
                ("company_id", "=", rec.company_id.id),
            )
            if rec.picking_type_use_filter_lots:
                rec.lot_id_domain = json.dumps(
                    default_domain + (("location_ids", "child_of", rec.location_id.id),)
                )
            else:
                rec.lot_id_domain = json.dumps(default_domain)

    @api.onchange("product_id", "company_id", "location_id")
    def _onchange_lot_domain(self):
        self._compute_lot_id_domain()
