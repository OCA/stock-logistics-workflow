from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class BillToPickingWizard(models.TransientModel):
    _name = "bill.to.picking.wizard"
    _description = "Wizard to add bill lines to Picking"

    picking_id = fields.Many2one(
        "stock.picking",
        string="Existing Picking",
        domain="[('partner_id', '=', partner_id), ('state', 'not in', ['done', 'cancel']), ('picking_type_code', '=', 'incoming')]",
    )
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True)

    def _get_active_lines(self):
        active_ids = self.env.context.get("active_ids", [])
        return self.env["picking.bill.line.match"].browse(active_ids)

    def action_add_to_picking(self):
        self.ensure_one()
        lines = self._get_active_lines()
        aml_ids = lines.aml_id.filtered("product_id")

        if not self.picking_id:
            self.picking_id = self.env["stock.picking"].create(
                {
                    "company_id": lines.aml_id[0].company_id.id,
                    "picking_type_id": self.env["stock.picking.type"]
                    .search(
                        [
                            ("code", "=", "incoming"),
                            ("company_id", "=", lines.aml_id[0].company_id.id),
                        ],
                        limit=1,
                    )
                    .id,
                    "partner_id": self.partner_id.id,
                }
            )

        if not aml_ids:
            raise UserError(
                _(
                    "No bill lines with products were selected to be added to the picking."
                )
            )

        for aml in aml_ids:
            self.env["stock.move"].create(
                {
                    "name": aml.name,
                    "product_id": aml.product_id.id,
                    "product_uom_qty": aml.unmatched_qty,
                    "quantity_done": aml.unmatched_qty,
                    "product_uom": aml.product_uom_id.id,
                    "picking_id": self.picking_id.id,
                    "location_id": self.picking_id.location_id.id,
                    "location_dest_id": self.picking_id.location_dest_id.id,
                    "invoice_line_ids": [Command.link(aml.id)],
                }
            )
        self.picking_id.button_validate()

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
