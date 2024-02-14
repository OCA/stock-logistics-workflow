# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move.line"

    sale_note = fields.Text(
        related="move_id.sale_note", related_sudo=False, store=True, readonly=False
    )
