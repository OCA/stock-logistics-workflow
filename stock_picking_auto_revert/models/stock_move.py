# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, exceptions, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_restrictions(self):
        # Restrictions before remove quants
        if self.returned_move_ids:
            raise exceptions.UserError(
                _(
                    "You cannot revert this stock picking. Move splited / with returned moves."
                )
            )
        if self.move_dest_ids or self.search([("move_dest_ids", "in", self.ids)]):
            origin_pickings = ", ".join(self.mapped("picking_id.name"))
            destination_pickings = ", ".join(
                self.mapped("move_dest_ids.picking_id.name")
            )
            raise exceptions.UserError(
                _(
                    "You cannot revert this stock picking. Its stock moves are linked to "
                    "other moves. Origin pickings: {origin_pickings}. "
                    "Destination pickings: {destination_pickings}."
                ).format(
                    origin_pickings=origin_pickings,
                    destination_pickings=destination_pickings,
                )
            )
