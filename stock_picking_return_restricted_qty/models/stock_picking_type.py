# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_return_qty = fields.Boolean(
        string="Restrict Return Quantity",
        help=(
            "Enable this option to restrict returning more quantities "
            "than delivered."
        ),
    )
