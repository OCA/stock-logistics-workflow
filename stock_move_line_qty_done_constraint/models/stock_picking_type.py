# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    qty_done_constraint = fields.Boolean(
        string="Restrict Quantity on Done Quantity",
        help="Check this if you want to restrict done quantity on stock moves."
        "It has to be lower or equal to 'Reserved' quantity.",
    )
