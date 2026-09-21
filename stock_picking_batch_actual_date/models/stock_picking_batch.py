# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingBatch(models.Model):
    _name = "stock.picking.batch"
    _inherit = ["stock.picking.batch", "stock.actual.date.mixin"]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if not rec.actual_date:
                continue
            rec.picking_ids.actual_date = rec.actual_date
        return res

    def write(self, vals):
        """Propagate `actual_date` to pickings and unset it on removed ones."""
        old_picking_map = {}
        if "picking_ids" in vals:
            old_picking_map = {batch.id: batch.picking_ids for batch in self}
        res = super().write(vals)
        if "actual_date" in vals or "picking_ids" in vals:
            for batch in self:
                batch.picking_ids.write({"actual_date": batch.actual_date})
                old_pickings = old_picking_map.get(batch.id, self.env["stock.picking"])
                removed_pickings = old_pickings - batch.picking_ids
                removed_pickings.write({"actual_date": False})
        return res

    def action_done(self):
        self.ensure_one()
        picks_before_done = self.picking_ids
        res = super().action_done()
        picks_detached = picks_before_done - self.picking_ids
        picks_detached.write({"actual_date": False})
        self.picking_ids.filtered(lambda x: x.actual_date != self.actual_date).write(
            {"actual_date": self.actual_date}
        )
        return res

    def _get_stock_moves(self):
        # Return an empty recordset to prevent duplicate `actual_date`
        # assignments on pickings' stock moves
        return self.env["stock.move"]
