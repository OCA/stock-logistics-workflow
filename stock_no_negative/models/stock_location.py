# ?? 2018 ForgeFlow (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    allow_negative_stock = fields.Boolean(
        string="Allow Negative Stock",
        help="Allow negative stock levels for the stockable products "
        "attached to this location.",
    )

    @api.constrains("allow_negative_stock")
    def _check_allow_negative_stock(self):
        for rec in self:
            if not rec.allow_negative_stock:
                rec.quant_ids.check_negative_qty()
