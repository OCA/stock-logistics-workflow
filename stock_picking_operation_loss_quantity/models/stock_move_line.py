# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command, first, float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_action_lose_quantity_allowed = fields.Boolean(
        compute="_compute_is_action_lose_quantity_allowed"
    )

    @api.depends("reserved_qty", "qty_done", "picking_id.picking_type_code")
    def _compute_is_action_lose_quantity_allowed(self):
        for rec in self:
            rec.is_action_lose_quantity_allowed = (
                rec.location_id.warehouse_id.use_loss_picking
                and (rec.qty_done - rec.reserved_qty < 0)
                and rec.state not in ("done", "draft")
                and rec.picking_id.picking_type_code != "incoming"
                and rec.picking_id.picking_type_id
                != rec.location_id.warehouse_id.loss_type_id
            )

    def action_lose_quantity(self):
        if any(not rec.is_action_lose_quantity_allowed for rec in self):
            raise UserError(_("You are not allowed to declare loss quantities"))
        return self._lose_quantity()

    def _prepare_loss_move_vals(self, unprocessed_qty):
        loss_pick_type = self.location_id.warehouse_id.loss_type_id
        return {
            "name": self.product_id.display_name,
            "product_id": self.product_id.id,
            "product_uom_qty": unprocessed_qty,  # This is the "demand"
            "product_uom": self.product_uom_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": loss_pick_type.default_location_dest_id.id,
            "lot_ids": [Command.set(self.lot_id.ids)] if self.lot_id else False,
        }

    def _prepare_loss_picking_vals(self, new_loss_move_vals):
        loss_pick_type = self.location_id.warehouse_id.loss_type_id
        return {
            "picking_type_id": loss_pick_type.id,
            "location_id": self.location_id.id,
            "location_dest_id": loss_pick_type.default_location_dest_id.id,
            "move_ids": [Command.create(new_loss_move_vals)],
        }

    def _find_loss_picking_moves_domain(self):
        loss_pick_type = self.location_id.warehouse_id.loss_type_id
        return [
            ("reserved_uom_qty", ">", 0.0),
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("lot_id", "=", self.lot_id.id),
            ("package_id", "=", self.package_id.id),
            ("owner_id", "=", self.owner_id.id),
            ("state", "not in", ("done", "cancel")),
            ("picking_type_id", "=", loss_pick_type.id),
            (
                "location_dest_id",
                "=",
                loss_pick_type.default_location_dest_id.id,
            ),
        ]

    def _find_loss_picking(self):
        similar_loss_lines = self.env["stock.move.line"].search(
            self._find_loss_picking_moves_domain()
        )
        loss_picking = first(similar_loss_lines.picking_id)
        return loss_picking

    def _create_loss_move_line(self, unprocessed_qty: float):
        self.ensure_one()
        loss_pick_type = self.location_id.warehouse_id.loss_type_id
        if not loss_pick_type:
            raise ValidationError(
                _(
                    "You don't have a Loss picking type enabled on your Warehouse! "
                    "Please check the 'Enable the Loss feature' in your warehouse "
                    "configuration."
                )
            )
        if not loss_pick_type.default_location_dest_id:
            raise ValidationError(
                _(
                    "You don't have any default destination set on your Loss picking type!"
                )
            )
        if (
            float_compare(
                unprocessed_qty, 0, precision_rounding=self.product_uom_id.rounding
            )
            <= 0
        ):
            raise ValidationError(
                _("You try to create a Loss picking without any loss quantity!")
            )

        new_loss_move_vals = self._prepare_loss_move_vals(unprocessed_qty)

        # Search for an already existing LOSS picking for this quant
        loss_picking = self._find_loss_picking()

        if loss_picking:
            new_loss_move = self.env["stock.move"].create(
                {**new_loss_move_vals, "picking_id": loss_picking.id}
            )
            # Use merge = False so that the number of move lines = the number
            # of loss declared for this quant
            new_loss_move._action_confirm(merge=False)
        else:
            loss_picking = self.env["stock.picking"].create(
                self._prepare_loss_picking_vals(new_loss_move_vals)
            )
            loss_picking.move_ids._action_confirm()

        if (
            self.location_id.warehouse_id.loss_auto_clear_threshold
            and len(loss_picking.move_ids)
            >= self.location_id.warehouse_id.loss_auto_clear_threshold
        ):
            quants_available_quantity = self.env["stock.quant"]._get_available_quantity(
                product_id=self.product_id,
                location_id=self.location_id,
                lot_id=self.lot_id,
                package_id=self.package_id,
                owner_id=self.owner_id,
            )
            if quants_available_quantity > 0:
                new_loss_move = self.env["stock.move"].create(
                    {
                        **new_loss_move_vals,
                        "product_uom_qty": quants_available_quantity,
                        "picking_id": loss_picking.id,
                    }
                )
                new_loss_move._action_confirm(merge=False)

        loss_picking.action_assign()
        return loss_picking

    def _unreserve_unprocessed_qty(self) -> float:
        self.ensure_one()
        unprocessed_qty = self.reserved_uom_qty - self.qty_done
        # Free the quantity that the operator was not able to do
        self.reserved_uom_qty = self.qty_done
        return unprocessed_qty

    def _lose_quantity(self):
        """
        This is the main function to call in order to declare a loss.

        It will check if operation is in progress (if operator has found the
        whole quantity, do not allow to declare a loss).

        Then, lock the quant that should be reserved by the loss picking and
        create that loss picking.
        """
        for line in self.filtered(lambda line: line.progress != 100.0):
            # Lock quants until the end of the transaction to avoid furter reservations
            quants = self.env["stock.quant"]._gather(
                product_id=line.product_id,
                location_id=line.location_id,
                lot_id=line.lot_id,
                package_id=line.package_id,
                owner_id=line.owner_id,
            )
            quants._lock_quants_for_loss()

            unprocessed_qty = line._unreserve_unprocessed_qty()
            loss_picking = line._create_loss_move_line(unprocessed_qty)
            loss_picking._schedule_loss_activity()

            if (
                float_compare(
                    line.reserved_uom_qty,
                    0,
                    precision_rounding=self.product_uom_id.rounding,
                )
                <= 0
            ):
                line.unlink()
