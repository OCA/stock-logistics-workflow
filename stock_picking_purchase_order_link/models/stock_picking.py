# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_view_purchase_order(self):
        """This function returns an action that display existing purchase order
        of given picking.
        """
        self.ensure_one()
        action = self.env.ref("purchase.purchase_form_action").read()[0]
        form = self.env.ref("purchase.purchase_order_form")
        action["views"] = [(form.id, "form")]
        action["res_id"] = self.purchase_id.id
        return action
