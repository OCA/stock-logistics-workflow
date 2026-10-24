# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # this is a technical field, making possible to search a picking by any restrict lot
    # defined on its line, from the web search bar.
    restrict_lot_id = fields.Many2one(
        related="move_ids.restrict_lot_id", string="Restrict Lot"
    )

    def _prepare_return_move_default_values(self, move_id):
        # The `stock.return.picking` wizard no longer exists on 20.0: returns are
        # built by the picking itself, so the lot restriction is carried here.
        vals = super()._prepare_return_move_default_values(move_id)
        if move_id.restrict_lot_id:
            vals["restrict_lot_id"] = move_id.restrict_lot_id.id
        return vals
