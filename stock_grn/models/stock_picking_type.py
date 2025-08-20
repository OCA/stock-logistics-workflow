# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_grn = fields.Integer(compute="_compute_count_picking_grn")

    def _compute_count_picking_grn(self):
        data = self.env["stock.picking"]._read_group(
            [
                ("grn_id", "!=", False),
                ("state", "not in", ("done", "cancel")),
                ("picking_type_id", "in", self.ids),
            ],
            ["picking_type_id"],
            aggregates=["__count"],
        )
        count = {picking_type.id: count for picking_type, count in data}
        for rec in self:
            rec.count_picking_grn = count.get(rec.id, 0)

    def get_action_picking_tree_grn(self):
        return self._get_action("stock_grn.action_picking_tree_grn")
