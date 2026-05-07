# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    interwarehouse_transfer_id = fields.Many2one(
        "stock.interwarehouse.transfer", string="Inter-WH Transfer", copy=False
    )

    def _create_backorder_picking(self):
        backorder = super()._create_backorder_picking()
        backorder.interwarehouse_transfer_id = self.interwarehouse_transfer_id
        return backorder
