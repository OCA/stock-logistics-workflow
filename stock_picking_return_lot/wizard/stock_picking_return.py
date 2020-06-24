# Copyright 2020 Iryna Vyshnevska Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        # return wizard cannot hold few lines for one move the implementation of
        # stock_account will raise singltone error, to propagate lot_id we are
        # mapping moves between pickings after move was created
        res = super()._create_returns()

        picking_returned = self.env["stock.picking"].browse(res[0])
        ml_ids_to_update = picking_returned.move_line_ids.ids
        moves_with_lot = self.product_return_moves.mapped(
            "move_id.move_line_ids"
        ).filtered(lambda l: l.lot_id)

        for line in moves_with_lot:
            ml = fields.first(
                picking_returned.move_line_ids.filtered(
                    lambda l: l.product_id == line.product_id
                    and l.id in ml_ids_to_update
                )
            )
            if ml and not ml.lot_id and (ml.product_uom_qty == line.qty_done):
                ml.lot_id = line.lot_id
            ml_ids_to_update.remove(ml.id)
        return res
