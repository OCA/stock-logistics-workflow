# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models
from odoo.exceptions import AccessError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def unlink(self):
        if not self.env.user.has_group(
            "stock_picking_unlink_group.group_stock_picking_unlink"
        ):
            raise AccessError(
                self.env._("You are not allowed to delete stock transfers.")
            )
        return super().unlink()
