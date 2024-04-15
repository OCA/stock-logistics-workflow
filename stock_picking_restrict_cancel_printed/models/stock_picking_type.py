# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_cancel_if_printed = fields.Boolean(
        string="Restrict cancelation if printed",
        help="When checked, the cancelation of a printed transfer will not be allowed",
        default=True,
    )
