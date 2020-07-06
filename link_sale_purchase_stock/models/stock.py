# Copyright 2020 KEMA SK, s.r.o. - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = self.env[
            "purchase.order.line"
        ]._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if "sale_line_id" not in res:
            res["sale_line_id"] = values.get("sale_line_id", False)
        return res


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    stock_move_ids = fields.One2many(
        "stock.move", "group_id", string="Related Stock Moves"
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            "product_id",
            "price_unit",
            "procure_method",
            "location_id",
            "location_dest_id",
            "product_uom",
            "restrict_partner_id",
            "scrapped",
            "origin_returned_move_id",
            "package_level_id",
            "propagate_cancel",
            "propagate_date",
            "propagate_date_minimum_delta",
            "delay_alert",
        ]

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        return [
            move.product_id.id,
            move.price_unit,
            move.procure_method,
            move.location_id,
            move.location_dest_id,
            move.product_uom.id,
            move.restrict_partner_id.id,
            move.scrapped,
            move.origin_returned_move_id.id,
            move.package_level_id.id,
            move.propagate_cancel,
            move.propagate_date,
            move.propagate_date_minimum_delta,
            move.delay_alert,
        ]
