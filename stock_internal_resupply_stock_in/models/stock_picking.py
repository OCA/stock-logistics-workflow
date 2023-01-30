# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        for rec in self:
            if rec.picking_type_id == rec.picking_type_id.warehouse_id.stock_in_type_id:
                rec.move_lines.procure_method = "make_to_order"
        return super().action_confirm()


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_stock_in = fields.Integer(compute="_compute_picking_stock_in")

    def _get_picking_stock_in_domain(self):
        self.ensure_one()
        return [
            ("picking_type_id", "=", self.id),
            ("state", "not in", ("done", "cancel")),
            (
                "location_dest_id",
                "=",
                self.company_id.internal_transit_location_id.id,
            ),
        ]

    def _compute_picking_stock_in(self):
        for rec in self:
            if rec.warehouse_id.out_type_id == rec:
                domain = rec._get_picking_stock_in_domain()
                rec.count_picking_stock_in = self.env["stock.picking"].search_count(
                    domain
                )
            else:
                rec.count_picking_stock_in = 0

    def get_action_picking_tree_stock_in(self):
        views = [
            (self.env.ref("stock.vpicktree").id, "tree"),
            (self.env.ref("stock.view_picking_form").id, "form"),
        ]
        return {
            "name": "Stock In Transfer",
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "view_mode": "tree, form",
            "res_model": "stock.picking",
            "views": views,
            "view_id": False,
            "target": "current",
            "domain": self._get_picking_stock_in_domain(),
        }
