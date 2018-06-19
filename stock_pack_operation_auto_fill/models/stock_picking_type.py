# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_fill_operation = fields.Boolean(
        string="Auto fill operations",
    )
    avoid_lot_assignment = fields.Boolean(
        string="Avoid auto-assignment of lots",
        default=True,
    )
