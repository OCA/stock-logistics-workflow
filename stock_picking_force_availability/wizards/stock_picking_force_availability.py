# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingForceAvailability(models.TransientModel):
    _name = "stock.picking.force_availability"
    _description = "Force availability on the current transfer."

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Current Transfer",
        readonly=True,
    )
    move_to_unreserve_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Moves To Unreserve",
        compute="_compute_move_to_unreserve_ids",
        help="Moves from other transfers that will be unreserve",
    )
    warning = fields.Char(compute="_compute_move_to_unreserve_ids")
    same_picking_type = fields.Boolean(
        string="Same operation type?",
        default=True,
    )
    assign_moves = fields.Boolean(
        string="Reserve moves right after?",
        help=(
            "Try to reserve back unreserved moves once goods have been "
            "reserved for the current transfer."
        ),
        default=True,
    )

    @api.model
    def default_get(self, fields_list):
        """'default_get' method overloaded."""
        res = super().default_get(fields_list)
        picking_model = self.env["stock.picking"]
        active_model = self.env.context.get("active_model")
        if active_model != "stock.picking":
            raise UserError(
                _("'{wizard_desc}' has to be open from a {picking_desc}.").format(
                    wizard_desc=self._name,
                    picking_desc=picking_model._name,
                )
            )
        picking_id = self.env.context.get("active_id")
        res["picking_id"] = picking_id
        picking_model.browse(picking_id).exists()
        return res

    @api.depends("picking_id", "same_picking_type")
    def _compute_move_to_unreserve_ids(self):
        move_model = self.env["stock.move"]
        for wiz in self:
            wiz.warning = wiz.move_to_unreserve_ids = False
            moves_to_assign = wiz.picking_id.move_lines.filtered_domain(
                [("state", "in", ("confirmed", "partially_available"))]
            )
            locations = moves_to_assign.location_id
            products = moves_to_assign.product_id
            picking_type = (
                moves_to_assign.picking_type_id if wiz.same_picking_type else None
            )
            moves_to_unreserve_ids = set()
            for location in locations:
                for product in products:
                    moves_to_unreserve_ids |= set(
                        move_model._get_moves_to_unreserve(
                            location=location,
                            product=product,
                            picking_types=picking_type,
                            extra_domain=[("id", "not in", moves_to_assign.ids)],
                        ).ids
                    )
            moves_to_unreserve = move_model.browse(moves_to_unreserve_ids)
            if not moves_to_unreserve:
                wiz.warning = _("Nothing to unreserve has been found.")
            else:
                wiz.move_to_unreserve_ids = moves_to_unreserve

    def validate(self):
        """Unreserve other moves and reserve goods for the current transfer."""
        self.ensure_one()
        moves_to_unreserve = self.move_to_unreserve_ids
        moves_to_unreserve._do_unreserve()
        self.picking_id.action_assign()
        if self.assign_moves:
            moves_to_unreserve.picking_id.filtered(
                lambda picking: picking.show_check_availability
            ).action_assign()
        return True
