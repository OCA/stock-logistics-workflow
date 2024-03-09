# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.fields import first


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        During picking creation on move picking assignation,
        transfer the move prioriry to the new created picking.

        If several moves are in recordset, use the max one.
        """
        values = super()._get_new_picking_values()
        if "priority" not in values:
            values.update({"priority": max(move.priority for move in self)})
        return values

    def _key_assign_picking(self):
        """
        Add priority in assignation keys for grouping if enabled
        """
        keys = super()._key_assign_picking()
        if self.picking_type_id.group_moves_per_priority:
            keys += (self.priority,)
        return keys

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        if self.picking_type_id.group_moves_per_priority:
            domain += [("priority", "=", first(self).priority)]
        return domain

    def _compute_priority(self):
        move_without_priority = self.filtered(lambda m: not m.priority)
        return super(StockMove, move_without_priority)._compute_priority()
