# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockDeviceType(models.Model):
    _inherit = "stock.device.type"

    split_mode = fields.Selection(
        selection_add=[("kit_quantity", "Kit Quantity")],
        ondelete={"kit_quantity": "set default"},
    )
