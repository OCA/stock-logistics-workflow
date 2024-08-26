# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveForceReservation(models.TransientModel):
    _name = "stock.move.force.reservation"

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Current Transfer",
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Current Move",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Current Product",
        readonly=True,
    )

    move_to_unreserve_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Moves To Unreserve",
        help="Moves from other transfers that will be unreserve",
    )
    total_quantity = fields.Float(compute="_compute_total_quantity")

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        active_id = self.env.context.get("active_id", False)
        stock_move = self.env["stock.move"].browse(active_id)
        rec.update(
            {
                "move_id": stock_move,
                "product_id": stock_move.product_id,
                "picking_id": stock_move.picking_id,
            }
        )
        return rec

    @api.depends("move_to_unreserve_ids")
    def _compute_total_quantity(self):
        total_quantity = 0
        for record in self.move_to_unreserve_ids:
            total_quantity += record.product_uom_qty
        self.total_quantity = total_quantity

    @api.onchange("move_id", "product_id")
    def onchange_move_id(self):
        if self.move_id and self.product_id:
            warehouse_id = self.picking_id.location_id.get_warehouse()
            move_ids = self.env["stock.move"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("state", "in", ["assigned", "partially_available"]),
                    ("id", "!=", self.move_id.id),
                    ("warehouse_id", "=", warehouse_id.id),
                ]
            )
            domain = {"move_to_unreserve_ids": [("id", "in", move_ids.ids)]}
            return {"domain": domain}

    def validate(self):
        moves_to_unreserve = self.move_to_unreserve_ids
        moves_to_unreserve._do_unreserve()
        self.picking_id.action_assign()
