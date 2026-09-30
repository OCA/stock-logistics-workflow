# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        domain=[("supplier_rank", ">", 0)],
        index=True,
        tracking=True,
        help="Supplier from whom this lot/serial number was received.",
    )
