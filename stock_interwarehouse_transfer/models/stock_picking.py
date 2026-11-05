# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    interwarehouse_transfer_id = fields.Many2one(
        "stock.interwarehouse.transfer",
        string="Inter-WH Transfer",
        compute="_compute_interwarehouse_transfer_id",
        store=True,
    )

    @api.depends("move_ids.interwh_transfer_line_id")
    def _compute_interwarehouse_transfer_id(self):
        for picking in self:
            transfer = picking.move_ids.interwh_transfer_line_id.transfer_id
            if len(transfer) == 1:
                picking.interwarehouse_transfer_id = transfer
            else:
                picking.interwarehouse_transfer_id = picking.interwarehouse_transfer_id
