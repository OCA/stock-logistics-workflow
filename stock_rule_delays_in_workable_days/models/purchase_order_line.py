# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    planned_expiry_date = fields.Date(
        "Planned expiry date", help="exact or minimal planned expired date"
    )
    planned_expiry_date_required = fields.Boolean(
        "Planned expiry date required",
        compute="_compute_planned_expiry_date_required",
        help="Technical fields to determine if planned expiry date is required or not "
        "on purchase order line",
    )

    @api.onchange("product_id", "date_planned", "planned_expiry_date_required")
    def onchange_planned_expiry_date(self):
        if (
            self.planned_expiry_date_required
            and self.product_id.expiration_time > 0
            and self.date_planned
        ):
            self.planned_expiry_date = self.date_planned + relativedelta(
                days=self.product_id.expiration_time
            )

    @api.depends(
        "product_id",
        "product_id.product_tmpl_id.tracking",
        "product_id.product_tmpl_id.use_expiration_date",
    )
    def _compute_planned_expiry_date_required(self):
        for line in self:
            line.planned_expiry_date_required = (
                line.product_id.product_tmpl_id.tracking != "none"
                and line.product_id.product_tmpl_id.use_expiration_date
            )

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if values.get("date_planned"):
            res["date_planned"] = values["date_planned"]

        if (
            product_id.product_tmpl_id.tracking != "none"
            and product_id.product_tmpl_id.use_expiration_date
            and res["date_planned"]
            and product_id.expiration_time > 0
        ):
            res["planned_expiry_date"] = res["date_planned"] + timedelta(
                days=product_id.expiration_time
            )

        return res

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        date_planned = self._beginning_of_day(values.get("date_planned"))
        lines = self.filtered(
            lambda line, date=date_planned: self._beginning_of_day(line.date_planned)
            == date
        )
        return super(PurchaseOrderLine, lines)._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )

    @api.model
    def _beginning_of_day(self, date):
        if not date:
            return None
        return date.date()
