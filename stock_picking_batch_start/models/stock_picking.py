# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def assign_batch_user(self, user_id):
        if self.env.company.stock_picking_assign_operator_at_start:
            return
        return super().assign_batch_user(user_id)
