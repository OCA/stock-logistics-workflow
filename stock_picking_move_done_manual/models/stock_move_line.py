# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.multi
    def action_move_manual_done_from_picking(self):
        for rec in self:
            rec.move_id.with_context(skip_backorder=True)._action_done()
            if rec.picking_id.state not in ["done", "cancel"]:
                rec.move_id.picking_id.action_assign()
