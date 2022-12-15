# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class StockQuantMoveWizard(models.TransientModel):
    _name = "stock.quant.move.wizard"
    _description = "Wizard to Move Quants"
    _check_company_auto = True

    line_ids = fields.One2many(
        "stock.quant.move.wizard.line", "wizard_id", string="Lines"
    )
    company_id = fields.Many2one("res.company", required=True)
    location_dest_id = fields.Many2one(
        "stock.location",
        string="Destination Location",
        domain="[('usage', '!=', 'view'), ('company_id', '=', company_id)]",
        check_company=True,
        required=True,
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    origin = fields.Char(string="Source Document")
    # Idea : add a bool option 'move even if reserved' (= current behavior)

    @api.onchange("picking_type_id")
    def picking_type_id_change(self):
        if self.picking_type_id and self.picking_type_id.default_location_dest_id:
            self.location_dest_id = self.picking_type_id.default_location_dest_id

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        assert self._context.get("active_model") == "stock.quant"
        company_id = self.env.company.id
        quants_ids = self._context.get("active_ids", [])
        quants = self.env["stock.quant"].browse(quants_ids)
        lines = []
        for quant in quants.filtered(
            lambda q: not q.package_id and q.company_id.id == company_id
        ):
            lines.append((0, 0, {"quant_id": quant.id, "quantity": quant.quantity}))
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "internal"), ("company_id", "=", company_id)], limit=1
        )
        res.update(
            {
                "line_ids": lines,
                "company_id": company_id,
                "picking_type_id": picking_type and picking_type.id or False,
            }
        )
        return res

    def run(self):
        self.ensure_one()
        picking_id = False
        if self.picking_type_id:
            picking_vals = self.env["stock.quant"]._prepare_move_to_stock_picking(
                self.location_dest_id, self.picking_type_id, origin=self.origin
            )
            picking_id = self.env["stock.picking"].create(picking_vals).id
        smo = self.env["stock.move"]
        for line in self.line_ids:
            quant = line.quant_id
            assert not quant.package_id
            vals = quant._prepare_move_to_stock_move(
                line.quantity, self.location_dest_id, picking_id, origin=self.origin
            )
            new_move = smo.create(vals)
            new_move._action_done()
            assert new_move.state == "done"
        action = {}
        if picking_id and self._context.get("run_show_picking"):
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock.stock_picking_action_picking_type"
            )
            action.update(
                {
                    "res_id": picking_id,
                    "view_mode": "form,tree,pivot",
                    "views": False,
                    "view_id": False,
                }
            )
        return action


class StockQuantMoveWizardLine(models.TransientModel):
    _name = "stock.quant.move.wizard.line"
    _description = "Lines of the wizard to move quants"

    wizard_id = fields.Many2one(
        comodel_name="stock.quant.move.wizard", string="Quant Move", ondelete="cascade"
    )
    quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Quant",
        required=True,
    )
    product_id = fields.Many2one(related="quant_id.product_id")
    quant_quantity = fields.Float(related="quant_id.quantity", string="On Hand Qty")
    quantity = fields.Float(string="Qty to Move", digits="Product Unit of Measure")
    uom_id = fields.Many2one(related="quant_id.product_id.uom_id")
    lot_id = fields.Many2one(related="quant_id.lot_id")
    src_location_id = fields.Many2one(
        related="quant_id.location_id", string="Current Location"
    )
