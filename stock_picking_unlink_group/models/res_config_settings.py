# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_allow_stock_picking_deletion = fields.Boolean(
        "Allow deletion of stock transfers",
        implied_group="stock_picking_unlink_group.group_stock_picking_unlink",
        group="stock.group_stock_user",
    )
