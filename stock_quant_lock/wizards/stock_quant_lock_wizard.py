# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantLockWizard(models.TransientModel):
    _name = "stock.quant.lock.wizard"
    _description = "Stock Quant Lock Wizard"

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        required=True,
        domain="[('allow_quant_lock', '=', True)]",
    )
    quant_ids = fields.Many2many(
        comodel_name="stock.quant",
        string="Quants",
        readonly=True,
    )

    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if self.env.context.get("active_model") == "stock.quant":
            vals["quant_ids"] = [(6, 0, self.env.context.get("active_ids", []))]
        return vals

    def action_lock(self):
        self.ensure_one()
        for quant in self.quant_ids:
            quant._lock_with_picking_type(self.picking_type_id)
        return {"type": "ir.actions.act_window_close"}
