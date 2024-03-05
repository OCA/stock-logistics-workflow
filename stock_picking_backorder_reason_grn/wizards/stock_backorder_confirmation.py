# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockBackorderConfirmation(models.TransientModel):

    _inherit = "stock.backorder.confirmation"

    def process(self):
        res = super().process()
        # We keep only pickings that were eligible for backorders creation and those
        # where backorder reason is configured to keep the GRN
        pickings_for_grn = self.backorder_confirmation_line_ids.filtered(
            lambda line: line.to_backorder and line.keep_grn
        ).mapped("picking_id")
        # Do one search before the loop
        backorders = self.env["stock.picking"].search(
            [("backorder_id", "in", pickings_for_grn.ids)]
        )
        for backorder in backorders:
            backorder.grn_id = pickings_for_grn.filtered(
                lambda pick: pick.id == backorder.backorder_id.id
            ).grn_id
        return res
