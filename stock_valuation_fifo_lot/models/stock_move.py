# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_common_svl_vals(self):
        """
        Prepare lots/serial numbers on stock valuation report
        """
        self.ensure_one()
        res = super()._prepare_common_svl_vals()
        res.update(
            {
                "lot_ids": [(6, 0, self.lot_ids.ids)],
            }
        )
        return res

    def _create_out_svl(self, forced_quantity=None):
        """
        Send context current move to _create_out_svl function
        """
        layers = self.env["stock.valuation.layer"]
        for move in self:
            move = move.with_context(used_in_move_id=move.id)
            layer = super(StockMove, move)._create_out_svl(
                forced_quantity=forced_quantity
            )
            layers |= layer
        return layers

    def _create_in_svl(self, forced_quantity=None):
        """
        1. Check stock move - Multiple lot on the stock move is not
           allowed for incoming transfer
        2. Change product standard price to first available lot price
        """
        layers = self.env["stock.valuation.layer"]
        for move in self:
            layer = super(StockMove, move)._create_in_svl(
                forced_quantity=forced_quantity
            )
            # Calculate standard price (Sorted by lot created date)
            if (
                move.product_id.cost_method == "fifo"
                and move.product_id.tracking != "none"
            ):
                all_candidates = move.product_id._get_all_candidates(
                    move.company_id, sort_by="lot_create_date"
                )
                if all_candidates:
                    move.product_id.sudo().with_company(
                        move.company_id.id
                    ).with_context(
                        disable_auto_svl=True
                    ).standard_price = all_candidates[
                        0
                    ].unit_cost
            layers |= layer
        return layers

    def _get_price_unit(self):
        """
        No PO, Get price unit from lot price
        """
        self.ensure_one()
        price_unit = super()._get_price_unit()
        if (
            not self.purchase_line_id
            and self.product_id.cost_method == "fifo"
            and len(self.lot_ids) == 1
        ):
            candidates = (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", self.product_id.id),
                        (
                            "lot_ids",
                            "in",
                            self.lot_ids.ids,
                        ),
                        ("quantity", ">", 0),
                        ("value", ">", 0),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )
            if candidates:
                price_unit = candidates[0].unit_cost
        return price_unit
