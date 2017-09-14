# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.model
    def _transfer_pickings_with_auto_move(self, auto_moves_by_pickings):
        """This function is meant to simulate what a user would normally
        transfer a picking from the user interface either partial processing
        or full processing.
        @params auto_moves_by_pickings: dict of moves grouped by pickings
        {stock.picking(id): stock.move(id1, id2, id3 ...), ...}
        """
        for picking in auto_moves_by_pickings:
            if len(picking.move_lines) != len(auto_moves_by_pickings[picking]):
                # Create a back order for remaning moves
                backorder_moves = \
                    picking.move_lines - auto_moves_by_pickings[picking]
                self._create_backorder(
                    picking=picking, backorder_moves=backorder_moves)

            # Create immediate transfer wizard so it will fill the qty_done
            # on the auto move linked operation
            wizard = self.env['stock.immediate.transfer'].create(
                {'pick_id': picking.id})
            wizard.process()

        return
