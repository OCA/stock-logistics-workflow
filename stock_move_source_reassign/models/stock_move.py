# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND

from odoo.addons.stock.models.stock_move import StockMove as Move
from odoo.addons.stock.models.stock_picking import Picking, PickingType


class StockMove(models.Model):
    _inherit = "stock.move"

    can_be_reassigned = fields.Boolean(
        compute="_compute_can_be_reassigned",
    )

    @api.depends("state")
    def _compute_can_be_reassigned(self):
        for move in self:
            move.can_be_reassigned = (
                self.env.user.has_group("stock_move_source_reassign.group_can_reassign")
                and move.picking_type_id.can_reassign
                and bool(move.state == "assigned")
            )

    def _check_can_be_reassigned(self):
        if any(not move.can_be_reassigned for move in self):
            raise ValidationError(_("You cannot reassign moves that are not reserved!"))

    def action_source_reassign(self):
        self._check_can_be_reassigned()
        context = self.env.context.copy()
        context["default_move_ids"] = self.ids
        # This can come from picking view context
        if "form_view_ref" in context:
            del context["form_view_ref"]
        return {
            "type": "ir.actions.act_window",
            "name": "Reassign",
            "res_model": "stock.move.reassign",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def _cancel_pickings_after_reassign(self):
        """
        If the original pickings are void, Odoo set them as draft.
        Cancel them.
        """

    def _source_reassign(
        self,
        destination_picking_type: PickingType,
        transfer_picking_type: PickingType,
        destination_picking: (Picking | bool) = False,
        strict=True,
        **kwargs
    ) -> tuple[Move, Move]:
        """
        This will reassign the concerned move to the destination picking.
        If the source location is different from the destination picking,
        the

        """
        self._check_can_be_reassigned()
        if not destination_picking:
            destination_picking = self.env["stock.picking"].browse()
        source_location = (
            destination_picking.location_id
            if destination_picking
            else destination_picking_type.default_location_src_id
        )
        reassigned_moves = self.browse()
        transfer_moves = self.browse()
        original_pickings = dict()
        for _package_level, moves in self.partition("package_level_id").items():
            original_picking = moves.picking_id
            original_pickings[original_picking] = moves
            force_transfer_picking = False
            transfer_move = self.browse()
            if any(
                move_line.location_id != moves.location_id
                for move_line in moves.move_line_ids
            ):
                # The source location for the concerned product is in a different location
                # than the move one
                force_transfer_picking = True
            moves._do_unreserve()
            if force_transfer_picking or (moves.location_id != source_location):
                transfer_move = moves._create_move_to_transfer_reassign(
                    picking_type=transfer_picking_type
                )
                transfer_move._action_confirm()
            # Assign the move to a new picking or the one passed as parameter
            moves._set_fields_before_reassign(
                destination_picking_type, destination_picking
            )
            if all(
                move._check_reassign_picking(destination_picking, strict)
                for move in moves
            ):
                moves.picking_id = destination_picking
            else:
                moves.picking_id = False
                moves.with_context(
                    not_reassign_picking_id=original_picking.id
                )._assign_picking()
            moves._action_assign()
            reassigned_moves |= moves
            transfer_moves |= transfer_move
        self._source_reassign_log_picking(original_pickings)
        to_cancel_pickings = self.env["stock.picking"].browse()
        for original_picking in original_pickings.keys():
            if not original_picking.move_ids and original_picking.state == "draft":
                to_cancel_pickings |= original_picking
        if to_cancel_pickings:
            to_cancel_pickings.action_cancel()
        return reassigned_moves, transfer_moves

    def _source_reassign_log_picking(self, original_pickings):
        """
        This will log in the original pickings chatter the moves that will be
        reassigned.
        """
        for original_picking, moves in original_pickings.items():
            move_names = ", ".join(moves.mapped("name"))
            picking_names = ", ".join(
                [picking._get_html_link() for picking in moves.picking_id]
            )
            message = _(
                "The following movements have been reassigned: %(move_names)s "
                "to the picking: %(picking_names)s",
                move_names=move_names,
                picking_names=picking_names,
            )
            original_picking.message_post(body=message)

    def _set_fields_before_reassign(
        self, destination_picking_type, destination_picking=False
    ):
        """
        Change here the mandatory fields that allow the movement to be reassigned
        to the new picking.
        """
        self.picking_type_id = destination_picking_type
        self.location_id = (
            destination_picking.location_id
            if destination_picking
            else destination_picking_type.default_location_src_id
        )

    def _check_reassign_picking(self, picking, strict=True):
        """
        This will check if the picking can be used for move reassignation

        This can be bypassed if needed by setting strict=False.
        """
        self.ensure_one()
        if strict:
            picking = picking.filtered_domain(
                self._search_picking_for_assignation_domain()
            )
        if not picking:
            return False
        return True

    def _create_move_to_transfer_reassign(self, picking_type):
        """
        This will create transfer moves from the original ones in order
        to move the products (or packages) to the new destination (that will be
        the source for the original picking).
        """
        transfer_moves = self.browse()
        for move in self:
            transfer_moves |= move.copy(
                {
                    "location_dest_id": picking_type.default_location_dest_id.id,
                    "picking_type_id": picking_type.id,
                    "picking_id": False,
                    # Add the transfer move to the origin moves of the destination one
                    "move_dest_ids": self.ids,
                }
            )

        return transfer_moves

    def _search_picking_for_assignation_domain(self):
        """
        This will exclude the picking we are coming from
        """
        domain = super()._search_picking_for_assignation_domain()
        # Don't reassign the move to the same picking
        not_reassign_picking_id = self.env.context.get("not_reassign_picking_id")
        if not_reassign_picking_id:
            domain = AND(
                [
                    domain,
                    [("id", "!=", not_reassign_picking_id)],
                ]
            )
        return domain
