# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """Prepares a new picking for this move as it could not be assigned to
        another picking.
        Add the customer from the procurement group.
        """
        res = super()._get_new_picking_values()
        res["customer_id"] = self.group_id.customer_id.id
        return res
