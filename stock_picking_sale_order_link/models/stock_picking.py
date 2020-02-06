# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_view_sale_order(self):
        """This function returns an action that display existing sales order
        of given picking.
        """
        self.ensure_one()
        action = self.env.ref("sale.action_orders").read()[0]
        form = self.env.ref("sale.view_order_form")
        action["views"] = [(form.id, "form")]
        action["res_id"] = self.sale_id.id
        return action
