# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _pre_action_done_hook(self):
        if self.env.context.get("show_immediate_warning"):
            pickings_to_immediate = self._get_pickings_to_immediate_transfer()
            if pickings_to_immediate:
                return (
                    pickings_to_immediate._action_generate_immediate_transfer_wizard()
                )
        return super()._pre_action_done_hook()

    def _get_pickings_to_immediate_transfer(self):
        """Return pickings that have reserved quantity but no move explicitly
        picked, and where all moves are fully reserved (no backorder scenario).
        """
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        pickings_to_immediate = self.browse()
        for picking in self:
            has_quantity = False
            has_pick = False
            is_partial = False
            for move in picking.move_ids:
                if move.state == "cancel":
                    continue
                if move.quantity:
                    has_quantity = True
                if (
                    float_compare(
                        move._get_picked_quantity(),
                        move.product_uom_qty,
                        precision_digits=prec,
                    )
                    < 0
                ):
                    # Partial move. Transfer will be handled
                    # in the backorder wizard.
                    is_partial = True
                    break
                if move.scrapped:
                    continue
                if move.picked:
                    has_pick = True
                if has_quantity and has_pick:
                    break
            if has_quantity and not has_pick and not is_partial:
                pickings_to_immediate |= picking
        return pickings_to_immediate

    def _action_generate_immediate_transfer_wizard(self):
        view = self.env.ref(
            "stock_picking_immediate_transfer_warning.view_immediate_transfer_warning"
        )
        return {
            "name": _("Immediate Transfer?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.immediate.transfer.warning",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context,
                default_pick_ids=[(4, p.id) for p in self],
            ),
        }
