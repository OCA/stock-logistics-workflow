# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models
from odoo.fields import first


class StockMoveReassign(models.TransientModel):
    _name = "stock.move.reassign"
    _description = "Stock Move Reassign"

    move_ids = fields.Many2many(
        comodel_name="stock.move",
        ondelete="cascade",
        readonly=True,
    )
    strict = fields.Boolean(
        compute="_compute_strict",
    )
    reassigned_move_ids = fields.Many2many(
        comodel_name="stock.move",
        ondelete="cascade",
        column1="wizard_id",
        column2="reassigned_move_id",
        relation="stock_move_reassign_reassigned_move_rel",
    )
    reassigned_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_reassigned_picking_ids",
    )
    transfer_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        ondelete="cascade",
    )
    package_level_ids = fields.Many2many(
        comodel_name="stock.package_level", ondelete="cascade", readonly=True
    )
    reassign_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        compute="_compute_reassign_picking_type_id",
        store=True,
        readonly=False,
        help="This is the operation type the system will look for a picking "
        "to reassign the selected products.",
    )
    reassign_transfer_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        compute="_compute_reassign_transfer_picking_type_id",
        store=True,
        help="This is the operation type that will be used to transfer the "
        "already resserved products to the new picking.",
    )
    destination_picking_domain = fields.Binary(
        compute="_compute_destination_picking_domain",
    )
    reassign_picking_type_domain = fields.Binary(
        compute="_compute_reassign_picking_type_domain",
    )
    reassign_transfer_picking_type_domain = fields.Binary(
        compute="_compute_reassign_transfer_picking_type_domain",
    )
    destination_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        ondelete="cascade",
        help="This is the picking to reassign the movements to. If no picking is "
        "provided, a new picking will be created.",
    )
    step = fields.Selection(
        [
            ("ask_picking_type", "Ask Picking Type"),
            ("ask_destination", "Ask Destination"),
            ("ask_transfer", "Ask Transfer"),
            ("result", "Result"),
        ],
        compute="_compute_step",
        store=True,
    )

    @api.depends("move_ids")
    def _compute_strict(self):
        for wizard in self:
            wizard.strict = first(wizard.move_ids).picking_type_id.can_reassign_strict

    @api.depends("reassigned_move_ids")
    def _compute_reassigned_picking_ids(self):
        for wizard in self:
            wizard.reassigned_picking_ids = wizard.reassigned_move_ids.picking_id

    @api.depends("move_ids")
    def _compute_reassign_picking_type_domain(self):
        for wizard in self:
            wizard.reassign_picking_type_domain = [
                ("code", "=", first(wizard.move_ids.picking_id).picking_type_code)
            ]

    @api.depends("move_ids")
    def _compute_reassign_transfer_picking_type_domain(self):
        for wizard in self:
            wizard.reassign_transfer_picking_type_domain = [("code", "=", "internal")]

    @api.depends("move_ids")
    def _compute_reassign_picking_type_id(self):
        # Compute a default value for the picking to reassign to
        for wizard in self:
            wizard.reassign_picking_type_id = (
                wizard.move_ids.picking_type_id.default_move_reassign_picking_type_id
            )

    @api.depends("move_ids")
    def _compute_reassign_transfer_picking_type_id(self):
        # Compute a default value for the transfer picking
        for wizard in self:
            wizard.reassign_transfer_picking_type_id = (
                wizard.move_ids.picking_type_id.default_move_reassign_transfer_picking_type_id
            )

    @api.depends("move_ids")
    def _compute_step(self):
        for wizard in self:
            wizard.step = "ask_picking_type"

    @api.depends("move_ids")
    def _compute_destination_picking_domain(self):
        for wizard in self:
            domain = [
                ("id", "not in", wizard.move_ids.picking_id.ids),
                ("picking_type_id", "=", wizard.reassign_picking_type_id.id),
                ("partner_id", "=", wizard.move_ids.partner_id.id),
                ("state", "not in", ("draft", "done", "cancel")),
            ]
            wizard.destination_picking_domain = domain

    def doit(self):
        for wizard in self:
            if wizard.step == "ask_picking_type":
                self.move_ids._check_can_be_reassigned()
                wizard.write({"step": "ask_destination"})
                return {
                    "type": "ir.actions.act_window",
                    "name": "Reassign",
                    "res_model": "stock.move.reassign",
                    "res_id": wizard.id,
                    "view_mode": "form",
                    "target": "new",
                }
            elif wizard.step == "ask_destination":
                self.move_ids._check_can_be_reassigned()
                wizard.write({"step": "ask_transfer"})
                return {
                    "type": "ir.actions.act_window",
                    "name": "Reassign",
                    "res_model": "stock.move.reassign",
                    "res_id": wizard.id,
                    "view_mode": "form",
                    "target": "new",
                }
            elif wizard.step == "ask_transfer":
                self.move_ids._check_can_be_reassigned()
                reassigned_moves, transfer_moves = wizard.move_ids._source_reassign(
                    wizard.reassign_picking_type_id,
                    wizard.reassign_transfer_picking_type_id,
                    wizard.destination_picking_id,
                    wizard.strict,
                )
                wizard.write(
                    {
                        "step": "result",
                        "reassigned_move_ids": [Command.set(reassigned_moves.ids)],
                        "transfer_picking_ids": [
                            Command.set(transfer_moves.picking_id.ids)
                        ],
                    }
                )
                return {
                    "type": "ir.actions.act_window",
                    "name": "Reassign",
                    "res_model": "stock.move.reassign",
                    "res_id": wizard.id,
                    "view_mode": "form",
                    "target": "new",
                }

        return True
