# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    bypass_reservation = fields.Boolean(
        string="Reserve over availability",
        help="If checked, products from this Picking Type will always be reserved "
        "even if you don't have enough stock (available stock will be reserved as "
        "usual).\nNote: Pickings will be reserved on Confirmation even if you don't "
        "have checked the option",
    )
