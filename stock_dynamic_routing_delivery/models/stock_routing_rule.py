# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRoutingRule(models.Model):
    _inherit = "stock.routing.rule"

    propagate_carrier = fields.Boolean(
        "Propagation of carrier",
        help="When ticked, carrier of shipment will be propagated.",
    )
