# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class BillToPickingWizard(models.TransientModel):
    _name = "bill.to.picking.wizard"
    _description = "Wizard to add bill lines to Picking"

    picking_id = fields.Many2one(
        "stock.picking",
        string="Existing Picking",
        domain=(
            "[('partner_id', '=', partner_id), ('state', 'not in', ['done', 'cancel']),"
            " ('picking_type_code', '=', 'incoming')]"
        ),
    )
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True)

    auto_validate = fields.Boolean(
        string="Auto-Validate Receipt",
        default=lambda self: self.env.company.auto_validate_matched_picking,
    )

    def _get_active_lines(self):
        active_ids = self.env.context.get("active_ids", [])
        return self.env["picking.bill.line.match"].browse(active_ids)

    def action_add_to_picking(self):
        self.ensure_one()
        lines = self._get_active_lines()
        aml_ids = lines.aml_id.filtered("product_id")

        if not aml_ids:
            raise UserError(_("No bill lines with products were selected."))

        if not self.picking_id:
            company = aml_ids[0].company_id
            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "incoming"),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )

            self.picking_id = self.env["stock.picking"].create(
                {
                    "company_id": company.id,
                    "picking_type_id": picking_type.id,
                    "partner_id": self.partner_id.id,
                    "location_id": picking_type.default_location_src_id.id
                    or self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": picking_type.default_location_dest_id.id,
                    "move_type": "direct",  # avoid conflict with ctx default_move_type
                }
            )

        for aml in aml_ids:
            move_vals = {
                "name": aml.name or aml.product_id.display_name,
                "product_id": aml.product_id.id,
                "product_uom_qty": aml.unmatched_qty,
                "product_uom": aml.product_uom_id.id,
                "picking_id": self.picking_id.id,
                "location_id": self.picking_id.location_id.id,
                "location_dest_id": self.picking_id.location_dest_id.id,
                "invoice_line_ids": [Command.link(aml.id)],
            }
            # Set quantity_done if auto-validating
            if self.auto_validate and not self.picking_id.origin:
                move_vals["quantity_done"] = aml.unmatched_qty

            self.env["stock.move"].create(move_vals)

        if self.picking_id.state == "draft":
            self.picking_id.action_confirm()

        # Auto Validate or just Assign
        if self.auto_validate and not self.picking_id.origin:
            self.picking_id.button_validate()
        else:
            self.picking_id.action_assign()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        action.update(
            {
                "view_mode": "form",
                "res_id": self.picking_id.id,
                "views": [[self.env.ref("stock.view_picking_form").id, "form"]],
            }
        )
        return action
