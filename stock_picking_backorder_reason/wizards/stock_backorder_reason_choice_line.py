# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class StockBackorderReasonChoiceLine(models.TransientModel):

    _name = "stock.backorder.reason.choice.line"
    _description = "Stock Backorder Reason Choice Line"

    wizard_id = fields.Many2one(
        comodel_name="stock.backorder.reason.choice",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Picking",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
