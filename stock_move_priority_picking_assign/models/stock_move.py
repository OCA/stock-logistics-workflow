# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        During picking creation on move picking assignation,
        transfer the move prioriry to the new created picking
        """
        values = super()._get_new_picking_values()
        if "priority" not in values:
            values.update({"priority": self.priority})
        return values
