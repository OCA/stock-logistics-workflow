# Copyright 2025 Camptocamp SA
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qty_picked = fields.Float(compute="_compute_qty_picked")

    @api.depends(
        "move_line_ids.picked",
        "move_line_ids.product_uom_id",
        "move_line_ids.qty_picked",
        "move_line_ids.quantity",
        "product_uom",
    )
    def _compute_qty_picked(self):
        for move in self:
            move.qty_picked = move._sum_ml_qty_picked()

    def _get_picked_quantity(self):
        if self._ml_has_qty_picked():
            return self.qty_picked
        return super()._get_picked_quantity()

    def _ml_has_qty_picked(self):
        return self.picked and any(ml.qty_picked for ml in self.move_line_ids)

    def _sum_ml_qty_picked(self):
        self.ensure_one()
        quantity = 0
        for move_line in self.move_line_ids.filtered("picked"):
            quantity += move_line.product_uom_id._compute_quantity(
                move_line.qty_picked, self.product_uom, round=False
            )
        return quantity

    def _align_quantity_with_qty_picked(self):
        self.move_line_ids._align_quantity_with_qty_picked()

    def _register_hook(self):
        super()._register_hook()

        def _patched__action_done(self, cancel_backorder=False):
            self._align_quantity_with_qty_picked()
            return _patched__action_done.origin(self, cancel_backorder)

        ModelClass = self.env.registry[self._name]
        method = _patched__action_done
        method.origin = ModelClass._action_done
        ModelClass._action_done = _patched__action_done

    def _unregister_hook(self):
        # pylint: disable=missing-return, except-pass
        super()._unregister_hook()
        try:
            ModelClass = self.env.registry[self._name]
            delattr(ModelClass, "_action_done")
        except AttributeError:
            pass
