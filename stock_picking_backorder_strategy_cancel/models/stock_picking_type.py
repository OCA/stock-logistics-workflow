# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    create_backorder = fields.Selection(
        selection_add=[("cancel", "Cancel")],
        ondelete={"cancel": "set default"},
    )
