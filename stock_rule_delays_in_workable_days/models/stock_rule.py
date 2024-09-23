# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import date, datetime, timedelta
from typing import Union

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.resource.models.resource import make_aware

from .weekday import WeekdaysEnum


class StockRule(models.Model):
    _inherit = "stock.rule"

    is_delay_in_workable_days = fields.Boolean(
        string="Delay in Workable Days",
        help="If checked, the delay will be calculated in workable days based on the"
        "calendars of both the source and the destination of the transfer "
        "(if provided).",
        default=False,
    )

    lead_times_by_day_ids = fields.One2many(
        "lead_times_by_day",
        "rule_id",
        string="Lead times by day",
        help="The lead time in days for the stock rule",
    )

    def _get_stock_move_values(
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
        self.ensure_one()
        stock_move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        if not self.is_delay_in_workable_days:
            return stock_move_values

        return {
            **stock_move_values,
            "date": self.compute_stock_move_date(
                values["date_planned"],
                -1 * self.delay,
            ),
        }

    def compute_stock_move_date(
        self,
        date_planned: Union[str, date, datetime],
        lead_time: Union[int, float],
    ) -> datetime:
        if not isinstance(date_planned, datetime):
            date_planned = fields.Datetime.to_datetime(date_planned)
        date_planned.replace(hour=0, minute=0, second=0, microsecond=0)
        if isinstance(lead_time, float):
            lead_time = round(lead_time)

        source_calendar = self.location_src_id.get_warehouse().calendar_id
        destination_calendar = self.location_id.get_warehouse().calendar_id

        calendar_resource = self.env["resource.calendar"]
        compute_transfer_dates = None
        if self.action == "pull":
            lead_time = -1 * lead_time
            compute_transfer_dates = (
                calendar_resource.compute_transfer_dates_from_target_received_date
            )
        elif self.action == "push":
            compute_transfer_dates = (
                calendar_resource.compute_transfer_dates_from_target_sent_date
            )

        if not compute_transfer_dates:
            return date_planned

        return compute_transfer_dates(
            date_planned,
            lead_time,
            source_calendar,
            destination_calendar,
        )["actual_sent_date"]

    @api.constrains("lead_times_by_day_ids")
    def _check_lead_times_by_day_ids(self):
        """
        Filter the lead_times_by_day_ids to ensure that we have at least one value
        for the lead time and that we don't have two lead times for the same day
        """
        for rule in self:
            for lead_time_by_day in rule.lead_times_by_day_ids:
                if (
                    len(
                        rule.lead_times_by_day_ids.filtered(
                            lambda d, day=lead_time_by_day: d.weekday == day.weekday
                        )
                    )
                    > 1
                ):
                    raise ValidationError(
                        _("You can't have two lead time for the same day")
                    )

    @api.model
    def _run_buy(self, procurements):
        self.env = self.env(
            context=dict(
                self.env.context,
                stock_rule_buy_update=True,
            )
        )
        for procurement, rule in procurements:
            self._update_procurement(procurement, rule)
        super()._run_buy(procurements)

    @api.model
    def _update_procurement(self, procurement, rule):
        self._update_procurement_supplierinfo_id(procurement)
        self._update_procurement_date_planned_and_date_order(procurement, rule)

    @api.model
    def _update_procurement_supplierinfo_id(self, procurement):
        """
        We want to try to find the correct supplier for a warehouse.
        For example, a "Croissant" can be bought from a supplier in Paris and another
        supplier in Lyon. So, if the order is for a warehouse in Paris, we want to
        use the supplier in Paris.

        So to do that, we need to pass as a parameter the warehouse_id to the
        _select_supplier method.
        """
        warehouse_id = procurement.values.get("warehouse_id", None)  # noqa: PD011
        if not warehouse_id:
            return
        if procurement.values.get("supplierinfo_id"):  # noqa: PD011
            return

        supplier = procurement.product_id.with_company(
            procurement.company_id.id
        )._select_seller(
            partner_id=procurement.values.get("supplierinfo_name"),  # noqa: PD011
            quantity=procurement.product_qty,
            date=max(
                procurement.values.get("date_planned").date(),  # noqa: PD011
                fields.Date.today(),
            ),
            uom_id=procurement.product_uom,
            params={"warehouse_id": warehouse_id},
        )
        if not supplier:
            return
        procurement.values["supplierinfo_id"] = supplier  # noqa: PD011

    @api.model
    def _update_procurement_date_planned_and_date_order(self, procurement, rule):
        """
        In the service workflow, we need to recompute the date_planned using the
        following parameters:
            - The event date
            - The expiration time of the product
            - The supplier calendar
            - The warehouse calendar

        The date_planned is recomputed using the following steps:
            1. Compute the limit date using the event date and the product's
               expiration time
            2. Compute the order dates using the supplier and warehouse calendars
            3. Use the computed order dates to update the purchase order's date_order
            4. Use the computed expected delivery date to update the date_planned of
               the purchase order line

        """
        if not rule.lead_times_by_day_ids:
            return
        consume_date = procurement.values.get(  # noqa: PD011
            "planned_consumed_date", False
        )
        deadline = procurement.values.get("date_deadline", False)  # noqa: PD011
        if not consume_date and not deadline:
            return
        planned_consumed_date = consume_date or deadline
        date_planned = procurement.values.get("date_planned")  # noqa: PD011
        product_id_expiration_time = procurement.product_id.expiration_time
        supplierinfo = procurement.values.get("supplierinfo_id")  # noqa: PD011
        supplier_calendar = (
            supplierinfo.name.supplier_calendar_id if supplierinfo else False
        )
        limit_date = planned_consumed_date - timedelta(days=product_id_expiration_time)
        if rule.is_delay_in_workable_days:
            results = self.env[
                "resource.calendar"
            ].compute_order_dates_from_target_received_date_working_days(
                date_planned,
                limit_date,
                rule._prepare_lead_times_by_day_values(),
                supplier_calendar,
                procurement.location_id.warehouse_id.calendar_id,
            )
        else:
            results = self.env[
                "resource.calendar"
            ].compute_order_dates_from_target_received_date(
                date_planned,
                limit_date,
                rule._prepare_lead_times_by_day_values(),
                supplier_calendar,
                procurement.location_id.warehouse_id.calendar_id,
            )
        if results is None:
            raise ValidationError(
                _(
                    "No delivery date found with the current configuration. "
                    "Please check the supplier calendar, the warehouse calendar, "
                    "the product expiration delay or adjust the event date."
                )
            )
        date_order, revert = make_aware(results["actual_order_date"])
        date_order_paris = date_order.astimezone(pytz.timezone("Europe/Paris"))
        date_order_paris_10_00 = date_order_paris.replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )
        date_order = revert(date_order_paris_10_00)
        current_datetime = datetime.now()
        if date_order < current_datetime:
            raise ValidationError(
                _(
                    "The order date is in the past. Please check the supplier "
                    "calendar, the warehouse calendar, the product expiration delay "
                    "or adjust the event date."
                )
            )

        procurement.values.update(  # noqa: PD011
            {
                "date_planned": results["expected_delivery_date"],
                "date_order": date_order,
            }
        )

    def _prepare_lead_times_by_day_values(self):
        return {
            WeekdaysEnum(day.weekday): day.value_ids.mapped("value")
            for day in self.lead_times_by_day_ids
        }

    def _make_po_get_domain(self, company_id, values, partner):
        """
        In the event workflow, The odoo order date filter is not True, as we compute
        the date_order using a custom logic so to ensure that we respect the odoo
        logic, we need to update the domain to include the precomputed date_order
        """
        domain = super()._make_po_get_domain(company_id, values, partner)
        date_order = values.get("date_order", False)
        delta_days = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_stock.delta_days_merge")
        )
        if date_order is False or delta_days is False:
            return domain
        # String config parameter is converted into an integer
        delta_days = int(delta_days)
        domain = tuple(
            [
                (field, operator, value)
                for (field, operator, value) in domain
                # We remove the following conditions on:
                #  - the date_order as the date_order is computed using a
                #    custom logic
                #  - the state to also merge with purchase orders other than the
                #    draft ones
                #  - the user_id since we also want to merge with manually
                #    created orders
                if field not in ["date_order", "state", "user_id"]
            ]
        )
        # We add back the condition on the state
        domain += (("state", "not in", ("done", "cancel")),)

        min_date_order = datetime.combine(
            date_order - relativedelta(days=delta_days),
            datetime.min.time(),
        )
        max_date_order = datetime.combine(
            date_order + relativedelta(days=delta_days),
            datetime.max.time(),
        )
        # We add back the condition on the date_order
        domain += (
            ("date_order", ">=", min_date_order),
            ("date_order", "<=", max_date_order),
        )
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        """
        In the event workflow, the odoo order date is not True, as we compute
        the order_date using a custom logic.
        So to ensure that the order_date meets the event workflow requirements,
        we need to update the order_date using the precomputed date_order.
        """
        res = super()._prepare_purchase_order(company_id, origins, values)
        # From odoo source:
        # Since the procurements are grouped if they share the same domain for
        # PO but the PO does not exist.
        # In this case, it will create the PO from the common procurement values.
        # The common values are taken from an arbitrary procurement.
        # In this case, the first.
        values = values[0]
        date_order = values.get("date_order", False)
        if date_order:
            res.update({"date_order": date_order})
        return res
