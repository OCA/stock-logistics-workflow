# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPickingCancel(models.TransientModel):
    _name = "stock.picking.cancel"
    _description = "Stock Picking Cancel"

    reason_id = fields.Many2one(
        comodel_name="stock.picking.cancel.reason", string="Reason", required=True
    )
    description = fields.Text()

    def confirm_cancel(self):
        self.ensure_one()
        act_close = {"type": "ir.actions.act_window_close"}
        picking_ids = self._context.get("active_ids")
        if picking_ids is None:
            return act_close
        if len(picking_ids) != 1:
            raise UserError(_("Please select exactly one transfer to cancel."))
        picking = self.env["stock.picking"].browse(picking_ids)
        picking.write(
            {
                "cancel_reason_id": self.reason_id.id,
                "cancel_description": self.description,
            }
        )
        picking.action_cancel()
        return act_close
