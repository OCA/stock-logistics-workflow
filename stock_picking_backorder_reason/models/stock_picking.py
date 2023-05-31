# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    backorder_reason_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        compute="_compute_backorder_reason_strategy",
        help="This is a technical field that says if a backorder is accepted"
        "depending on partner configuration accordingly with picking type one.",
    )

    @api.depends(
        "picking_type_id.backorder_reason",
        "picking_type_id.backorder_reason_sale",
        "picking_type_id.backorder_reason_purchase",
        "partner_id.sale_reason_backorder_strategy",
        "partner_id.purchase_reason_backorder_strategy",
    )
    def _compute_backorder_reason_strategy(self):
        pickings_sale = self.filtered("picking_type_id.backorder_reason_sale")
        for picking in pickings_sale:
            picking.backorder_reason_strategy = (
                picking.partner_id.sale_reason_backorder_strategy
            )
        pickings_purchase = self.filtered("picking_type_id.backorder_reason_purchase")
        for picking in pickings_purchase:
            picking.backorder_reason_strategy = (
                picking.partner_id.purchase_reason_backorder_strategy
            )
        # Remaining pickings
        self.browse(
            set(self.ids) - set(pickings_sale.ids) - set(pickings_purchase.ids)
        ).backorder_reason_strategy = False

    def _check_backorder_reason(self):
        return self.filtered("picking_type_id.backorder_reason")

    def _action_backorder_reason(self, show_transfers=False):
        view = self.env.ref(
            "stock_picking_backorder_reason.stock_backorder_choice_view_form"
        )
        return {
            "name": _("Choose a reason for backorder"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.backorder.reason.choice",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context,
                default_show_transfers=show_transfers,
                default_picking_ids=[(4, p.id) for p in self],
            ),
        }

    def _pre_action_done_hook(self):
        if not self.env.context.get("skip_backorder_reason"):
            # Check if backorder is needed and then if reason is needed
            pickings_with_backorder = self._check_backorder()
            pickings_with_reason = pickings_with_backorder._check_backorder_reason()
            if pickings_with_reason:
                return pickings_with_reason._action_backorder_reason(
                    show_transfers=self._should_show_transfers()
                )
        return super()._pre_action_done_hook()
