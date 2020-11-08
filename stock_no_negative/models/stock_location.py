# ?? 2018 Eficent (https://www.eficent.com)
# @author Jordi Ballester <jordi.ballester@eficent.com.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        help="Allow negative stock levels for the stockable products "
        "attached to this location.")

    @api.multi
    def _is_negative_allowed(self):
        self.ensure_one()
        return self.allow_negative_stock or self.usage not in ['internal', 'transit']
