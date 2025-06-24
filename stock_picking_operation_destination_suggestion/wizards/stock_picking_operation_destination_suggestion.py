# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.tools import ValidationError
from odoo.tools.float_utils import float_compare


class StockPickingOperationDestinationSuggest(models.TransientModel):

    _name = "stock.picking.operation.destination.suggestion"
    _description = "Stock Picking Destination Suggestion"

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        required=True,
        default=lambda self: self._get_default_picking_id(),
        readonly=True,
        ondelete="cascade",
    )

    destination_location_suggestion_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Suggested Destination Locations",
        compute="_compute_destination_location_suggestion_ids",
    )
    chosen_location_suggestion_id = fields.Many2one(
        comodel_name="stock.location",
        ondelete="cascade",
    )
    chosen_location_suggestion_domain = fields.Binary(
        compute="_compute_chosen_location_suggestion_domain",
    )

    move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        compute="_compute_move_line_ids",
        readonly=False,
    )

    def _get_default_picking_id(self):
        if self.env.context.get("active_model") != "stock.picking":
            raise ValidationError(
                _(
                    "You are not launching the destination suggestion from a Stock Picking"
                )
            )
        active_id = self.env.context.get("active_id")
        return self.env["stock.picking"].browse(active_id)

    @api.depends("destination_location_suggestion_ids")
    def _compute_chosen_location_suggestion_domain(self):
        for wizard in self:
            wizard.chosen_location_suggestion_domain = [
                ("id", "in", wizard.destination_location_suggestion_ids.ids)
            ]

    @api.depends("picking_id.destination_location_suggestion_ids")
    def _compute_destination_location_suggestion_ids(self):
        for wizard in self:
            wizard.destination_location_suggestion_ids = (
                wizard.picking_id.destination_location_suggestion_ids
            )

    @api.depends("picking_id.move_line_ids.qty_done")
    def _compute_move_line_ids(self):
        """
        Move lines for those location destination suggestion can be applied
        """
        for wizard in self:
            wizard.move_line_ids = wizard.picking_id.move_line_ids.filtered(
                lambda line: float_compare(
                    line.qty_done,
                    0.0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0
            )

    def doit(self):
        """
        Assign the destination location to all candidate operations
        """
        for wizard in self:
            wizard.move_line_ids.location_dest_id = wizard.chosen_location_suggestion_id
        action = {"type": "ir.actions.act_window_close"}
        return action
