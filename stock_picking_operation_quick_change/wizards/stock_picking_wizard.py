# Copyright 2017 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingOperationWizard(models.TransientModel):
    _name = "stock.picking.operation.wizard"
    _description = "Stock Picking Operation Wizard"

    def _prepare_default_values(self, picking):
        return {
            "picking_id": picking.id,
            "location_dest_id": picking.location_dest_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context["active_model"]
        active_ids = self.env.context["active_ids"] or []
        picking = self.env[active_model].browse(active_ids)
        res.update(self._prepare_default_values(picking))
        return res

    def _default_old_dest_location_id(self):
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.browse(self.env.context["active_ids"])
        first_move_line = pickings.mapped("move_line_ids")[:1]
        return first_move_line.location_dest_id.id

    def _get_allowed_locations(self):
        return ["internal"]

    def _get_allowed_location_domain(self):
        return [("usage", "in", self._get_allowed_locations())]

    def _get_allowed_picking_states(self):
        return ["assigned"]

    picking_id = fields.Many2one(comodel_name="stock.picking")
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Actual destination location",
        required=True,
        readonly=True,
    )
    old_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Old destination location",
        default=_default_old_dest_location_id,
        domain=lambda self: self._get_allowed_location_domain(),
    )
    new_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="New destination location",
        required=True,
        domain=lambda self: self._get_allowed_location_domain(),
    )
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_allowed_product_ids",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('id', 'in', allowed_product_ids)]",
    )
    change_all = fields.Boolean(
        help="Check if you want change all operations without filter "
        "by old location",
    )

    @api.depends("picking_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            record.allowed_product_ids = record.picking_id.move_lines.mapped(
                "product_id"
            )

    def check_allowed_pickings(self, pickings):
        forbidden_pickings = pickings.filtered(
            lambda x: x.state not in self._get_allowed_picking_states()
        )
        if forbidden_pickings:
            raise UserError(
                _(
                    "You can not change operations destination location if "
                    "picking state is not in %s"
                )
                % ",".join(self._get_allowed_picking_states())
            )
        pickings_with_chained_moves = pickings.filtered(
            lambda x: x.move_lines.mapped("move_dest_ids")
        )
        if pickings_with_chained_moves:
            raise UserError(
                _(
                    "You cannot change destination location if any of the moves "
                    "has a destination move."
                )
            )

    def action_apply(self):
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.browse(self.env.context["active_ids"])
        self.check_allowed_pickings(pickings)
        move_lines = pickings.mapped("move_line_ids")

        vals = {"location_dest_id": self.new_location_dest_id.id}
        if self.change_all:
            # Write all operations destination location
            move_lines.write(vals)
        else:
            matched_op = move_lines
            # Only write operations destination location if the location is
            # the same that old location value
            if self.old_location_dest_id:
                matched_op = matched_op.filtered(
                    lambda x: x.location_dest_id == self.old_location_dest_id
                )
            # Only write operations destination location if the product is the same
            if self.product_id:
                matched_op = matched_op.filtered(
                    lambda x: x.product_id == self.product_id
                )
            matched_op.write(vals)
        return {"type": "ir.actions.act_window_close"}
