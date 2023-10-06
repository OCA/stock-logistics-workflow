# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPickingOperationLossQuantity(models.TransientModel):

    _name = "stock.picking.operation.loss.quantity"
    _description = "Wizard to declare product loss quantitites on picking operations"

    # This contains move as move lines too as the process can be triggered
    # from one or the other.
    move_id = fields.Many2one(
        comodel_name="stock.move",
        ondelete="cascade",
    )
    move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        compute="_compute_move_line_ids",
        readonly=False,
        store=True,
    )

    @api.depends("move_id")
    def _compute_move_line_ids(self):
        for wizard in self:
            wizard.move_line_ids = wizard.move_id.move_line_ids

    def action_lose_quantity(self):
        self.ensure_one()
        # We don't have lots on movement, so let the process occurs
        # automatically
        if not self.move_id.lot_ids:
            return self._lose_quantity()

    @api.model
    def _update_loss_picking(self, loss_picking, quantity):
        loss_picking.move_ids.update(
            {
                "product_uom_qty": quantity,
                "quantity_done": quantity,
            }
        )

    @api.model
    def _validate_loss_picking(self, loss_picking):
        loss_picking.action_confirm()
        loss_picking.action_assign()
        return True

    def _check_lines_for_loss(
        self, operations_for_loss, lines, raise_if_nothing_for_loss=False
    ):
        if operations_for_loss != lines:
            not_found_for_loss_products_message = [
                _(
                    "Picking: %(picking)s Product: %(product)s",
                    picking=line.picking_id.name,
                    product=line.product_id.name,
                )
                for line in lines - operations_for_loss
            ]
            message = _(
                "No quantity found for loss movement for: \n %(products)s",
                products="\n".join(not_found_for_loss_products_message),
            )
            if raise_if_nothing_for_loss:
                raise UserError(message)
            _logger.info(message)

    @api.model
    def _get_matching_line_keys(self):
        """
        This return a list of field names that should be equivalent on the
        former line and the new one to be updated
        """
        return ["product_id", "location_id", "lot_id", "owner_id"]

    def _lose_quantity(self, raise_if_nothing_for_loss=True):
        """
        This is the main function to call in order to declare a loss.

        It will check if operation is in progress (if operator has found the
        whole quantity, do not allow to declare a loss).

        Then, lock the quant that should be reserved by the loss picking and
        create that loss picking.

        At the end, delete the unavailable move line.
        """
        for group_key, lines in self.move_line_ids._group_move_lines_for_loss().items():
            operations_for_loss = lines.filtered(
                lambda line: not line.progress == 100.0
            )
            if not operations_for_loss:
                continue
            self._check_lines_for_loss(
                operations_for_loss,
                lines,
                raise_if_nothing_for_loss=raise_if_nothing_for_loss,
            )
            # Lock quants until the end of the transaction to avoid furter reservations
            quants = self.env["stock.quant"]._gather(
                group_key.product_id,
                group_key.location_id,
                lot_id=group_key.lot_id,
                package_id=group_key.package_id,
                owner_id=group_key.owner_id,
            )
            quants._lock_quants_for_loss()

            lines._split_for_loss()
            loss_picking = lines._create_loss_picking(group_key)
            self._validate_loss_picking(loss_picking)
            lines.unlink()
