# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_view_sale_order(self):
        """This function returns an action that display existing sales order
        of given picking.
        """
        self.ensure_one()
        # Remove default_picking_id to avoid defaults get
        # https://github.com/odoo/odoo/blob/e4d22d390c8aa8edf757e36704a9e04b2b89f115/
        # addons/stock/models/stock_move.py#L410
        ctx = self.env.context.copy()
        ctx.pop("default_picking_id", False)
        return self.with_context(ctx).sale_id.get_formview_action()
