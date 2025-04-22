# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    move_line_label_report_id = fields.Many2one(
        string="Detailed operation label report",
        comodel_name="ir.actions.report",
        domain=[("model", "=", "stock.move.line")],
        help="Choose a custom label template for this operation type. It will enable "
        "printing from the detailed operations",
    )
