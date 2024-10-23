# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def write(self, vals):
        if "priority" in vals:
            self.move_ids.write({"priority": False})
        return super().write(vals)
