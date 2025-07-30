# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class StockShipmentComposerWizard(models.TransientModel):
    _name = "stock.shipment.composer.wizard"
    _description = "Wizard to Create Shipment Composer"

    picking_type_id = fields.Many2one(
        "stock.picking.type", required=True, string="Operation Type", readonly=True
    )
    partner_id = fields.Many2one("res.partner", readonly=True)
    line_ids = fields.One2many(
        "stock.shipment.composer.wizard.line",
        "wizard_id",
        string="Shipment Lines",
    )
    move_ids = fields.Many2many("stock.move", compute="_compute_move_ids", store=True)

    @api.depends("line_ids.move_id")
    def _compute_move_ids(self):
        for rec in self:
            rec.move_ids = rec.line_ids.move_id

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_ids = self.env.context.get("active_ids", [])
        moves = self.env["stock.move"].browse(move_ids)
        if any(state in ["done", "cancel"] for state in moves.mapped("state")):
            raise UserError(
                _(
                    "Please select stock moves that are not in 'Done' or 'Cancelled' state."
                )
            )
        picking_types = moves.mapped("picking_type_id")
        if len(picking_types) > 1:
            raise UserError(
                _("Please select stock moves with the same Operation Type.")
            )
        partners = moves.mapped("partner_id")
        if not partners:
            raise UserError(_("Please select stock moves with the partner."))
        if len(partners) > 1:
            raise UserError(_("All selected stock moves must have the same Partner."))
        partner = partners[0]
        res.update(
            {
                "picking_type_id": picking_types.id,
                "partner_id": partner.id,
                "line_ids": [Command.create({"move_id": m.id}) for m in moves],
            }
        )
        return res

    def action_create_composer(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You must have at least one shipment line."))
        composer = self.env["stock.shipment.composer"].create(
            {
                "partner_id": self.partner_id.id,
                "picking_type_id": self.picking_type_id.id,
                "line_ids": [
                    Command.create(
                        {
                            "move_id": line.move_id.id,
                            "quantity": line.quantity,
                            "remarks": line.remarks,
                        }
                    )
                    for line in self.line_ids
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.shipment.composer",
            "view_mode": "form",
            "res_id": composer.id,
            "target": "current",
        }
