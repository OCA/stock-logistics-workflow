# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    priority = fields.Selection(
        selection_add=[("-1", "Not urgent"), ("0",)], ondelete={"-1": "set default"}
    )
