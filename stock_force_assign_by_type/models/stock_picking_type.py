# Copyright 2024 Tecnativa S.L. - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    force_reservation = fields.Boolean(
        help="Check this box to force the reservation of stock for this picking type. "
        "When checked, stock will be automatically reserved for all operations of this type."
    )
