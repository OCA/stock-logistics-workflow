# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMoveChangeSourceLocation(models.TransientModel):
    _name = "stock.move.change.source.location.wizard"
    _description = "Stock Move Change Source Location Wizard"

    def _prepare_default_values(self, picking):
        warehouse = picking.location_id.get_warehouse()
        return {"warehouse_view_location_id": warehouse.view_location_id.id}

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context["active_model"]
        active_ids = self.env.context["active_ids"] or []
        picking = self.env[active_model].browse(active_ids)
        res.update(self._prepare_default_values(picking))
        return res

    def _default_old_location_id(self):
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.browse(self.env.context["active_ids"])
        first_move_line = pickings.mapped("move_lines")[:1]
        return first_move_line.location_id.id

    def _get_allowed_old_location_domain(self):
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.browse(self.env.context.get("active_ids", []))
        return [("id", "in", pickings.mapped("move_lines.location_id").ids)]

    def _get_allowed_new_location_domain(self):
        stock_picking_obj = self.env["stock.picking"]
        picking = stock_picking_obj.browse(self.env.context.get("active_ids", []))
        warehouse = picking.location_id.get_warehouse()
        return [
            ("id", "child_of", warehouse.view_location_id.id),
            ("usage", "=", "internal"),
        ]

    def _get_allowed_states(self):
        return ["waiting", "partially_available", "confirmed", "assigned"]

    warehouse_view_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Warehouse View Location",
        required=True,
        readonly=True,
    )
    old_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Old location",
        default=_default_old_location_id,
        domain=lambda self: self._get_allowed_old_location_domain(),
    )
    new_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="New location",
        required=True,
        domain=_get_allowed_new_location_domain,
    )
    moves_to_change = fields.Selection(
        selection=[
            ("all", "Change All moves"),
            ("matched", "Change only moves with matched OLD location"),
            ("manual", "Select moves to change"),
        ],
        string="Operations to change",
        required=True,
        default="all",
        help="Select which kind of selection of the moves you want to do",
    )
    move_lines = fields.Many2many("stock.move", string="Move lines")

    def _check_allowed_pickings(self, pickings):
        forbidden_pickings = pickings.filtered(
            lambda x: x.state not in self._get_allowed_states()
        )
        if forbidden_pickings:
            raise UserError(
                _(
                    "You can not change move source location if "
                    "picking state is not in %s"
                )
                % ", ".join(self._get_allowed_states())
            )

    def _check_allowed_moves(self, moves):
        forbidden_moves = moves.filtered(
            lambda x: x.state not in self._get_allowed_states()
        )
        if forbidden_moves:
            raise UserError(
                _(
                    "You can not change move source location if "
                    "the move state is not in %s"
                )
                % ", ".join(self._get_allowed_states())
            )
        if any([move.move_orig_ids for move in moves]):
            raise UserError(
                _(
                    "You cannot change source location if any of the moves "
                    "has an origin move."
                )
            )

    def action_apply(self):
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.browse(self.env.context["active_ids"])
        self._check_allowed_pickings(pickings)
        move_lines = pickings.mapped("move_lines")

        vals = {"location_id": self.new_location_id.id}
        if self.moves_to_change == "all":
            moves_to_change = move_lines
        elif self.moves_to_change == "matched":
            # Only write operations destination location if the location is
            # the same that old location value
            moves_to_change = move_lines.filtered(
                lambda x: x.location_id == self.old_location_id
            )
        else:
            # Only write operations destination location on the selected moves
            moves_to_change = self.move_lines

        self._check_allowed_moves(moves_to_change)

        # Unreserve moves first
        moves_to_change._do_unreserve()
        # Change source location
        moves_to_change.write(vals)
        # Check availability afterwards
        moves_to_change._action_assign()
        return {"type": "ir.actions.act_window_close"}
