# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    interwarehouse_transfer_id = fields.Many2one(
        "stock.interwarehouse.transfer", string="Inter-WH Transfer", copy=False
    )

    def _create_backorder(self):
        backorders = super()._create_backorder()
        for backorder in backorders:
            backorder.interwarehouse_transfer_id = (
                backorder.backorder_id.interwarehouse_transfer_id
            )
        return backorders
