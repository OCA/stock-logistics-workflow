# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_picking_return_lot_restrict = fields.Boolean(
        string="Restrict lot that can be selected based on those used in the move",
    )
