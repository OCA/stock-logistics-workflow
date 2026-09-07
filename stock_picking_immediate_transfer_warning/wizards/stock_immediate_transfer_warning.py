# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockImmediateTransferWarningLine(models.TransientModel):
    _name = "stock.immediate.transfer.warning.line"
    _description = "Immediate Transfer Warning Line"

    immediate_transfer_warning_id = fields.Many2one(
        "stock.immediate.transfer.warning",
        "Immediate Transfer Warning",
    )
    picking_id = fields.Many2one("stock.picking", "Transfer")


class StockImmediateTransferWarning(models.TransientModel):
    _name = "stock.immediate.transfer.warning"
    _description = "Immediate Transfer Warning"

    pick_ids = fields.Many2many("stock.picking", "stock_picking_immediate_rel")
    immediate_transfer_warning_line_ids = fields.One2many(
        "stock.immediate.transfer.warning.line",
        "immediate_transfer_warning_id",
        string="Immediate Transfer Warning Lines",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "immediate_transfer_warning_line_ids" in fields_list and res.get("pick_ids"):
            res["immediate_transfer_warning_line_ids"] = [
                (0, 0, {"picking_id": pick_id}) for pick_id in res["pick_ids"][0][2]
            ]
        return res

    def process(self):
        pickings_to_validate = self.env.context.get("button_validate_picking_ids")
        if pickings_to_validate:
            return (
                self.env["stock.picking"]
                .browse(pickings_to_validate)
                .with_context(show_immediate_warning=False)
                .button_validate()
            )
        return True
