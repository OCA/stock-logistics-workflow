# Copyright 2017 ACSONE SA/NV
# Copyright 2018 JARSA Sistemas S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    action_pack_op_auto_fill_allowed = fields.Boolean(
        compute="_compute_action_pack_operation_auto_fill_allowed"
    )
    auto_fill_operation = fields.Boolean(
        string="Auto fill operations",
        related="picking_type_id.auto_fill_operation",
    )

    @api.depends("state", "move_line_ids")
    def _compute_action_pack_operation_auto_fill_allowed(self):
        """
        The auto fill button is allowed only in ready state, and the
        picking have pack operations.
        """
        for rec in self:
            rec.action_pack_op_auto_fill_allowed = (
                rec.state == "assigned" and rec.move_line_ids
            )

    def _check_action_pack_operation_auto_fill_allowed(self):
        if any(not r.action_pack_op_auto_fill_allowed for r in self):
            raise UserError(
                _(
                    "Filling the operations automatically is not possible, "
                    "perhaps the pickings aren't in the right state "
                    "(Partially available or available)."
                )
            )

    def action_pack_operation_auto_fill(self):
        """
        Fill automatically pack operation for products with the following
        conditions:
            - the package is not required, the package is required if the
            the no product is set on the operation.
            - the operation has no qty_done yet.
        """
        self._check_action_pack_operation_auto_fill_allowed()
        operations = self.mapped("move_line_ids")
        operations_to_auto_fill = operations.filtered(
            lambda op: (
                op.product_id
                and not op.qty_done
                and (
                    not op.lots_visible
                    or not op.picking_id.picking_type_id.avoid_lot_assignment
                )
            )
        )
        for op in operations_to_auto_fill:
            op.qty_done = op.product_uom_qty
