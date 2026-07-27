# Copyright 2026 Abubakarafghan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    sow_packing_summary = fields.Char(
        string="Deprecated Packing Field (Keep for Safe DB Upgrade)",
    )
    packing_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="lot_id.packing_uom_id",
        string="Packing UoM",
        store=True,
        help="Original packing unit of measure stored on the lot.",
    )
    packing_qty = fields.Float(
        compute="_compute_packing_qty",
        digits="Product Unit of Measure",
        help="On-hand quantity converted to the lot packing UoM.",
    )

    @api.depends("quantity", "packing_uom_id", "product_uom_id")
    def _compute_packing_qty(self):
        for quant in self:
            if quant.packing_uom_id and quant.quantity:
                try:
                    quant.packing_qty = quant.product_uom_id._compute_quantity(
                        quant.quantity, quant.packing_uom_id
                    )
                except UserError:
                    quant.packing_qty = 0.0
            else:
                quant.packing_qty = 0.0
