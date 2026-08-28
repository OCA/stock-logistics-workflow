# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_standard_price(self, product_id, closing_id):
        price = 0

        closing_line_id = self.env["stock.close.period.line"].search(
            [("close_id", "=", closing_id.id), ("product_id", "=", product_id.id)],
            limit=1,
        )

        if closing_line_id:
            price = closing_line_id.price_unit

        return price

    def _get_evaluation_method_exist(self, product_id, closing_id):
        closing_line_id = self.env["stock.close.period.line"].search(
            [("close_id", "=", closing_id.id), ("product_id", "=", product_id.id)],
            limit=1,
        )

        if closing_line_id and closing_line_id.evaluation_method:
            return True
        else:
            return False

    def _get_cost_stock_move_production(self, closing_line_id):
        closing_id = closing_line_id.close_id
        product_id = closing_line_id.product_id
        bom = self.env["mrp.bom"].sudo()._bom_find(product_id)[product_id]
        skip = False

        if bom:
            total = 0
            boms_to_recompute = self.env["mrp.bom"].search(
                [
                    ("company_id", "=", closing_line_id.company_id.id),
                    "|",
                    ("product_id", "in", product_id.ids),
                    "&",
                    ("product_id", "=", False),
                    ("product_tmpl_id", "in", product_id.mapped("product_tmpl_id").ids),
                ]
            )
            total += product_id._get_extra_cost(bom)
            for opt in bom.operation_ids:
                duration_expected = (
                    opt.workcenter_id._get_expected_duration(product_id)
                    + opt.time_cycle * 100 / opt.workcenter_id.time_efficiency
                )
                total += (duration_expected / 60) * opt._total_cost_per_hour()
            for line in bom.bom_line_ids:
                if line._skip_bom_line(product_id):
                    continue

                # Compute recursive if line has 'child_line_ids'
                if line.child_bom_id and line.child_bom_id in boms_to_recompute:
                    child_total = line.product_id._compute_bom_price(
                        line.child_bom_id, boms_to_recompute=boms_to_recompute
                    )
                    total += (
                        line.product_id.uom_id._compute_price(
                            child_total, line.product_uom_id
                        )
                        * line.product_qty
                    )
                else:
                    # If product in doesn't have price in close period and in route have
                    # Manufacture skip
                    if (
                        self._get_standard_price(line.product_id, closing_id) == 0
                        and self.env.ref("mrp.route_warehouse0_manufacture").id
                        in line.product_id.route_ids.ids
                        and not self._get_evaluation_method_exist(
                            line.product_id, closing_id
                        )
                    ):
                        skip = True
                    total += (
                        line.product_id.uom_id._compute_price(
                            self._get_standard_price(line.product_id, closing_id),
                            line.product_uom_id,
                        )
                        * line.product_qty
                    )

            if not skip:
                closing_line_id.price_unit = total
                closing_line_id.evaluation_method = "production"

        if not skip and closing_line_id.price_unit == 0:
            closing_line_id.price_unit = product_id._get_cost()
            closing_line_id.evaluation_method = "standard"

    def _recompute_cost_stock_move_production(self, closing_id):
        _logger.info("[1/2] Start recompute cost product production")

        # search only lines not elaborated
        closing_line_ids = self.env["stock.close.period.line"].search(
            [
                ("close_id", "=", closing_id.id),
                ("evaluation_method", "!=", "manual"),
                # ("product_qty", ">", 0),  # all lines must be here to compute costs
                # ("price_unit", "=", 0),  # this was for elaborate only not already
                # done lines, which we instead want to check always
            ]
        )

        # proceed lines to be manufactured as they depend on the previous, starting
        # from the inner child to the most external (purchased lines are already
        # computed)
        product_order = closing_line_ids.mapped("product_id")._get_product_order()
        for closing_line_id in closing_line_ids.sorted(
            key=lambda x: product_order[x.product_id.id]
        ):
            product_id = closing_line_id.product_id

            # skip if the product doesn't have a bom (it's purchased)
            if not self.env["mrp.bom"]._bom_find(product_id)[product_id]:
                continue

            # imposta il metodo di calcolo
            if closing_id.force_standard_price:
                self._get_cost_stock_move_standard(closing_line_id)
            else:
                self._get_cost_stock_move_production(closing_line_id)

            self.env.cr.commit()  # pylint: disable=E8102
        _logger.info("[1/2] Finish add standard cost product")

    def recompute_average_cost_period_production(self, closing_id):
        _logger.info("Recompute average cost period. Making in 2 phases:")
        _logger.info("[1/2] Recompute cost product production")
        _logger.info("[2/2] Write results")

        self._recompute_cost_stock_move_production(closing_id)
        self._write_results(closing_id)

        _logger.info("End recompute average cost product")

    def _check_consistency(self, closing_line_id):
        result = super()._check_consistency(closing_line_id)
        if self.env["mrp.bom"]._bom_find(closing_line_id.product_id)[
            closing_line_id.product_id
        ]:
            return False
        return result
