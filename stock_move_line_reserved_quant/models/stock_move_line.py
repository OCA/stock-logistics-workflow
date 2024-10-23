# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    reserved_quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Reserved Quant",
        index=True,
        help="This is the quant reserved by this stock movement",
    )
