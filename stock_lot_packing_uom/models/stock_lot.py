# Copyright 2026 Abubakarafghan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    packing_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Packing UoM",
        help="Unit of measure originally used to receive this lot "
        "(for example box or pack).",
    )
    received_qty = fields.Float(
        string="Original Received Qty",
        help="Quantity originally received when this lot was created, "
        "expressed in the packing UoM.",
        digits="Product Unit of Measure",
    )
