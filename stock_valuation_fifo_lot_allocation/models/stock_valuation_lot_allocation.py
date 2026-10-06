# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockValuationLotAllocation(models.Model):
    _name = "stock.valuation.lot.allocation"
    _description = "Stock Valuation Lot Allocation"
    _order = "actual_date, id"

    lot_id = fields.Many2one(
        "stock.lot",
        "Lot/Serial Number",
        required=True,
        index=True,
        ondelete="cascade",
    )
    valuation_layer_id = fields.Many2one(
        "stock.valuation.layer",
        "Valuation Layer",
        required=True,
        index=True,
        ondelete="cascade",
    )
    allocated_amount = fields.Monetary(
        help="Share of the valuation layer value that is charged to the lot/serial. "
        "Written once when the layer is created and never recomputed."
    )
    # Related and stored rather than copied: for landed costs and revaluations the
    # journal entry is created after the layer, and the layer prefers the posted
    # entry's date, so the actual date is only settled later.
    actual_date = fields.Date(related="valuation_layer_id.actual_date", store=True)
    # Not related to the layer's description, as the balancing rows created by the
    # backfill (see stock.valuation.layer) need a label of their own.
    description = fields.Char()
    product_id = fields.Many2one(related="valuation_layer_id.product_id", store=True)
    company_id = fields.Many2one(related="valuation_layer_id.company_id", store=True)
    currency_id = fields.Many2one(related="valuation_layer_id.currency_id")
