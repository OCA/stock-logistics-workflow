# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # this is a technical field, making possible to search a picking by any restrict lot
    # defined on its line, from the web search bar.
    restrict_lot_id = fields.Many2one(
        related="move_ids.restrict_lot_id", string="Restrict Lot"
    )
