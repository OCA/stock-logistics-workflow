# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    can_plan_batches = fields.Boolean(
        string="Can plan batches",
        compute="_compute_can_plan_batches",
        help="Shows if this Batch can plan Batches",
    )
    origin_batches_count = fields.Integer(
        string="Origin batches count",
        compute="_compute_origin_batches_count",
        help="Number of Batches of the origin moves",
    )

    @api.depends(
        "state",
        "picking_ids",
        "picking_ids.move_ids.move_orig_ids",
        "picking_ids.move_ids.move_orig_ids.picking_id",
        "picking_ids.move_ids.move_orig_ids.picking_id.picking_type_id.plan_batch",
        "picking_ids.move_ids.move_orig_ids.picking_id.picking_type_id.auto_batch",
    )
    def _compute_can_plan_batches(self):
        """Check if this batch can plan batches"""
        self.can_plan_batches = False
        for record in self:
            if record.state != "in_progress":
                continue
            origin_pickings = self.mapped(
                "picking_ids.move_ids.move_orig_ids.picking_id"
            ).with_context(plan_batch=True)
            # If no origin pickings, nothing can be planned
            if not origin_pickings:
                continue
            for picking in origin_pickings:
                if not picking.picking_type_id.plan_batch:
                    # Check first if picking type allows batch planning
                    continue
                if picking._is_auto_batchable():
                    record.can_plan_batches = True
                else:
                    for move_line in picking.move_line_ids:
                        if move_line._is_auto_waveable():
                            record.can_plan_batches = True
                            break
                if record.can_plan_batches:
                    break

    @api.depends("picking_ids.move_ids.move_orig_ids.picking_id.batch_id")
    def _compute_origin_batches_count(self):
        """Count number of batches that are on the origin moves"""
        for record in self:
            record.origin_batches_count = len(
                record.picking_ids.move_ids.move_orig_ids.picking_id.batch_id
            )

    def action_plan_batches(self):
        """Plan Batches on batches that can_plan_batches is True."""
        # All calls to picking_type.auto_batch will be true due to plan_batch context
        batches = self.filtered("can_plan_batches").with_context(plan_batch=True)
        origin_pickings = batches.picking_ids.move_ids.move_orig_ids.picking_id
        for picking in origin_pickings:
            picking._find_auto_batch()
        origin_pickings.move_line_ids._auto_wave()
        return batches.action_view_origin_batches()

    def action_view_origin_batches(self):
        """Return an action to see origin moves batches or waves"""
        batches = self.picking_ids.move_ids.move_orig_ids.picking_id.batch_id
        action_vals = {
            "name": self.env._("Planned Origin Batches"),
            "res_model": "stock.picking.batch",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", batches.ids)],
            "context": self._context,
            "views": [[False, "list"], [False, "kanban"], [False, "form"]],
            "view_mode": "list,kanban,form",
        }
        if len(batches) == 1:
            action_vals.update(
                {
                    "views": [[False, "form"]],
                    "view_mode": "form",
                    "res_id": batches[0].id,
                }
            )
        return action_vals
