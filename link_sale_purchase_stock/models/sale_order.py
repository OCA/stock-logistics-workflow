# Copyright 2020 KEMA SK, s.r.o. - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order_count = fields.Integer(
        "Number of Purchase Order Generated",
        compute="_compute_purchase_order_count",
        groups="purchase.group_purchase_user",
    )

    @api.depends(
        "order_line.purchase_line_ids.order_id",
        "procurement_group_id.stock_move_ids.created_purchase_line_id.order_id",
    )
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(self._get_purchase_orders())

    def _get_purchase_orders(self):
        return (
            self.order_line.purchase_line_ids.order_id
            | self.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id
        )

    def action_view_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids = self._get_purchase_orders().ids
        action = {
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
        }
        if len(purchase_order_ids) == 1:
            action.update(
                {"view_mode": "form", "res_id": purchase_order_ids[0]}
            )
        else:
            action.update(
                {
                    "name": _("Purchase Order generated from %s" % self.name),
                    "domain": [("id", "in", purchase_order_ids)],
                    "view_mode": "tree,form",
                }
            )
        return action
