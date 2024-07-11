# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.fields import Command


class StockPicking(models.Model):

    _inherit = "stock.picking"

    backorder_reason_strategy = fields.Selection(
        selection=[
            ("create", "Create"),
            ("cancel", "Cancel"),
            ("transparent_cancel", "Transparent Cancel"),
        ],
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
        transparent_pickings = (pickings_sale | pickings_purchase).filtered(
            lambda p: p.picking_type_id.backorder_reason_transparent_cancel
            and p.backorder_reason_strategy == "cancel"
        )
        transparent_pickings.update({"backorder_reason_strategy": "transparent_cancel"})
        # Remaining pickings
        self.browse(
            set(self.ids)
            - set(pickings_sale.ids)
            - set(pickings_purchase.ids)
            - set(transparent_pickings.ids)
        ).backorder_reason_strategy = False

    def _check_backorder_reason(self):
        return self.filtered("picking_type_id.backorder_reason")

    def _action_backorder_transparent_cancel(self):
        return (
            self.env["stock.backorder.reason.choice"]
            .new(
                {
                    "picking_ids": [Command.set(self.ids)],
                    "choice_line_ids": [
                        Command.create({"picking_id": pick_id}) for pick_id in self.ids
                    ],
                }
            )
            .apply()
        )

    def _action_backorder_reason(self, show_transfers=False):
        if self.backorder_reason_strategy == "transparent_cancel":
            return (
                self.env["stock.backorder.reason.choice"]
                .new(
                    {
                        "picking_ids": [Command.set(self.ids)],
                        "choice_line_ids": [
                            Command.create({"picking_id": pick_id})
                            for pick_id in self.ids
                        ],
                    }
                )
                .apply()
            )
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

    def _check_transparent_cancel(self):
        return self.filtered(
            lambda p: p.backorder_reason_strategy == "transparent_cancel"
        )

    def _pre_action_done_hook(self):
        if not self.env.context.get("skip_backorder_reason"):
            # Check if backorder is needed and then if reason is needed
            pickings_with_backorder = self._check_backorder()
            pickings_with_transparent_cancel = self._check_transparent_cancel()
            if pickings_with_transparent_cancel:
                return self._action_backorder_transparent_cancel()
            pickings_with_reason = pickings_with_backorder._check_backorder_reason()
            if pickings_with_reason:
                return pickings_with_reason._action_backorder_reason(
                    show_transfers=self._should_show_transfers()
                )
        return super()._pre_action_done_hook()

    def button_validate(self):
        """
        In case of transparent cancel, we can pass to context 'picking_ids_not_to_backorder'
        value to let Odoo manage that case.
        """
        pickings_with_backorder = self._check_backorder()
        picking_not_to_backorder = pickings_with_backorder.filtered(
            lambda p: p.backorder_reason_strategy == "cancel"
        )._check_transparent_cancel()
        picking_ids_not_to_backorder = self.env.context.get(
            "picking_ids_not_to_backorder"
        )
        if picking_ids_not_to_backorder:
            # Don't override an existing context value but add records to it
            picking_not_to_backorder |= self.browse(picking_ids_not_to_backorder)
        if picking_not_to_backorder:
            new_self = self.with_context(
                picking_ids_not_to_backorder=picking_not_to_backorder.ids
            )
            return super(StockPicking, new_self).button_validate()
        else:
            return super().button_validate()
