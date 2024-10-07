# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import datetime
from unittest import mock
from unittest.mock import patch

import pytz
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

from ..models.weekday import WeekdaysEnum
from .common import CommonStockPurchaseOrderDateRule


@mock.patch(
    "odoo.addons.stock_rule_delays_in_workable_days.models.stock_rule."
    "StockRule.compute_stock_move_date"
)
class TestStockRuleGetStockMoveValues(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_route = cls.env["stock.location.route"].create(
            {
                "name": "Stock Route",
            }
        )
        cls.stock_picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Stock Picking Type",
                "code": "internal",
                "sequence_code": "sequence_code",
            }
        )
        cls.location_src = cls.env["stock.location"].create(
            {
                "name": "Source",
                "usage": "internal",
            }
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Destination",
                "usage": "internal",
            }
        )
        cls.stock_rule = cls.env["stock.rule"].create(
            {
                "name": "Stock Rule",
                "action": "pull_push",
                "picking_type_id": cls.stock_picking_type.id,
                "location_src_id": cls.location_src.id,
                "location_id": cls.location.id,
                "route_id": cls.stock_route.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.company = cls.env.ref("base.main_company")

    def test_get_stock_move_values_delay_not_in_workable_days(
        self,
        compute_stock_move_date_mock,
    ):
        self.stock_rule.action = "pull"
        self.stock_rule.is_delay_in_workable_days = False
        self.stock_rule.delay = 1
        self.stock_rule._get_stock_move_values(
            self.product,
            1,
            self.product_uom,
            self.location,
            "name",
            "origin",
            self.company,
            {"date_planned": "2024-01-10"},
        )
        compute_stock_move_date_mock.assert_not_called()

    def test_get_stock_move_values(
        self,
        compute_stock_move_date_mock,
    ):
        self.stock_rule.action = "pull"
        self.stock_rule.is_delay_in_workable_days = True
        self.stock_rule.delay = 3
        self.stock_rule._get_stock_move_values(
            self.product,
            1,
            self.product_uom,
            self.location,
            "name",
            "origin",
            self.company,
            {"date_planned": "2024-01-10"},
        )
        compute_stock_move_date_mock.assert_called_with("2024-01-10", -3)


@mock.patch(
    "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
    "ResourceCalendar.compute_transfer_dates_from_target_received_date"
)
@mock.patch(
    "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
    "ResourceCalendar.compute_transfer_dates_from_target_sent_date"
)
class TestStockRuleComputeStockMoveDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_route = cls.env["stock.location.route"].create(
            {
                "name": "Stock Route",
            }
        )
        cls.stock_picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Stock Picking Type",
                "code": "internal",
                "sequence_code": "sequence_code",
            }
        )
        cls.calendar_src = cls.env["resource.calendar"].create(
            {
                "name": "Source Calendar",
            }
        )
        cls.warehouse_src = cls.env["stock.warehouse"].create(
            {
                "name": "Source",
                "code": "source",
                "calendar_id": cls.calendar_src.id,
            }
        )
        cls.location_src = cls.env["stock.location"].create(
            {
                "name": "Source",
                "usage": "internal",
            }
        )
        cls.warehouse_src.view_location_id = cls.location_src
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Destination Calendar",
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Destination",
                "code": "destination",
                "calendar_id": cls.calendar.id,
            }
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Destination",
                "usage": "internal",
            }
        )
        cls.warehouse.view_location_id = cls.location
        cls.stock_rule = cls.env["stock.rule"].create(
            {
                "name": "Stock Rule",
                "action": "pull",
                "picking_type_id": cls.stock_picking_type.id,
                "location_src_id": cls.location_src.id,
                "location_id": cls.location.id,
                "route_id": cls.stock_route.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.company = cls.env.ref("base.main_company")

    def test_compute_stock_move_date_push_pull(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        date_planned = fields.Datetime.to_datetime("2024-01-10")
        self.stock_rule.action = "pull_push"
        date = self.stock_rule.compute_stock_move_date(date_planned, 0)
        self.assertEqual(date, date_planned)
        mock_compute_transfer_dates_from_target_sent_date.assert_not_called()
        mock_compute_transfer_dates_from_target_received_date.assert_not_called()

    def test_compute_stock_move_date_zero_lead_time_push(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        date_planned = fields.Datetime.to_datetime("2024-01-10")
        self.stock_rule.action = "push"
        self.stock_rule.compute_stock_move_date(date_planned, 0)
        mock_compute_transfer_dates_from_target_sent_date.assert_called_with(
            date_planned,
            0,
            self.calendar_src,
            self.calendar,
        )
        mock_compute_transfer_dates_from_target_received_date.assert_not_called()

    def test_compute_stock_move_date_zero_lead_time_pull(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        date_planned = fields.Datetime.to_datetime("2024-01-10")
        self.stock_rule.action = "pull"
        self.stock_rule.compute_stock_move_date(date_planned, 0)
        mock_compute_transfer_dates_from_target_sent_date.assert_not_called()
        mock_compute_transfer_dates_from_target_received_date.assert_called_with(
            date_planned,
            0,
            self.calendar_src,
            self.calendar,
        )

    def test_compute_stock_move_date_positive_lead_time(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        date_planned = fields.Datetime.to_datetime("2024-01-10")
        self.stock_rule.action = "push"
        self.stock_rule.compute_stock_move_date(date_planned, 3)
        mock_compute_transfer_dates_from_target_sent_date.assert_called_with(
            date_planned,
            3,
            self.calendar_src,
            self.calendar,
        )
        mock_compute_transfer_dates_from_target_received_date.assert_not_called()

    def test_compute_stock_move_date_negative_lead_time(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        date_planned = fields.Datetime.to_datetime("2024-01-10")
        self.stock_rule.action = "pull"
        self.stock_rule.compute_stock_move_date(date_planned, -3)
        mock_compute_transfer_dates_from_target_sent_date.assert_not_called()
        mock_compute_transfer_dates_from_target_received_date.assert_called_with(
            date_planned,
            3,
            self.calendar_src,
            self.calendar,
        )

    def test_compute_stock_param_types_conversion(
        self,
        mock_compute_transfer_dates_from_target_sent_date,
        mock_compute_transfer_dates_from_target_received_date,
    ):
        self.stock_rule.action = "push"
        self.stock_rule.compute_stock_move_date("2024-01-10", 3.4)
        mock_compute_transfer_dates_from_target_sent_date.assert_called_with(
            fields.Datetime.to_datetime("2024-01-10"),
            3,
            self.calendar_src,
            self.calendar,
        )
        mock_compute_transfer_dates_from_target_received_date.assert_not_called()


class TestStockRule(CommonStockPurchaseOrderDateRule):
    def test_prepare_purchase_order(self):
        res = self.stock_rule._prepare_purchase_order(
            company_id=self.env.ref("base.main_company"),
            origins="SO0001",
            values=[
                {
                    "supplier": self.product_id.seller_ids[0],
                    "date_planned": "2024-02-01 00:00:00",
                    "date_order": "2024-01-01 00:00:00",
                }
            ],
        )
        self.assertEqual(res["date_order"], "2024-01-01 00:00:00")

    @patch(
        "odoo.addons.purchase_stock.models.stock_rule.StockRule._prepare_purchase_order",
        return_value={"date_order": "2025-01-01 00:00:00"},
    )
    def test_prepare_purchase_order_without_date_order(
        self, mock_prepare_purchase_order
    ):
        res = self.stock_rule._prepare_purchase_order(
            company_id=self.env.ref("base.main_company"),
            origins="SO0001",
            values=[
                {
                    "supplier": self.product_id.seller_ids[0],
                    "date_planned": "2024-02-01 00:00:00",
                    "date_order": False,
                }
            ],
        )
        self.assertEqual(res["date_order"], "2025-01-01 00:00:00")

    @freeze_time("2024-01-01")
    def test_make_po_get_domain(self):
        date_order = datetime.now()
        res = self.stock_rule._make_po_get_domain(
            company_id=self.env.ref("base.main_company"),
            values={
                "date_planned": "2024-02-01 00:00:00",
                "date_order": date_order,
                "supplier": self.product_id.seller_ids[0],
            },
            partner=self.partner_supplier,
        )
        self.assertIn(
            ("date_order", ">=", datetime.combine(date_order, datetime.min.time())), res
        )
        self.assertIn(
            ("date_order", "<=", datetime.combine(date_order, datetime.max.time())), res
        )

    @freeze_time("2024-01-01")
    def test_test_make_po_get_domain_without_delta_days_merge(self):
        self.env["ir.config_parameter"].search(
            [("key", "=", "purchase_stock.delta_days_merge")]
        ).unlink()
        date_order = datetime.now()
        res = self.stock_rule._make_po_get_domain(
            company_id=self.env.ref("base.main_company"),
            values={
                "date_planned": "2024-02-01 00:00:00",
                "date_order": date_order,
                "supplier": self.product_id.seller_ids[0],
            },
            partner=self.partner_supplier,
        )
        for domain in res:
            self.assertNotEqual(domain[0], "date_order")

    @patch(
        "odoo.addons.purchase_stock.models.stock_rule.StockRule._make_po_get_domain",
        return_value=[],
    )
    def test_test_make_po_get_domain_without_date_order(self, mock_make_po_get_domain):
        res = self.stock_rule._make_po_get_domain(
            company_id=self.env.ref("base.main_company"),
            values={
                "date_planned": "2024-02-01 00:00:00",
                "date_order": False,
                "supplier": self.product_id.seller_ids[0],
            },
            partner=self.partner_supplier,
        )
        self.assertEqual(res, [])

    def _prepare_lead_times_by_day_values(self):
        res = self.stock_rule._prepare_lead_times_by_day_values()
        self.assertEqual(
            res,
            {
                WeekdaysEnum.Tuesday: [12, 14],
                WeekdaysEnum.Friday: [10],
            },
        )

    def test_check_lead_times_by_day_ids(self):
        with self.assertRaises(ValidationError) as e:
            self.stock_rule.write(
                {
                    "lead_times_by_day_ids": [
                        (
                            0,
                            0,
                            {
                                "weekday": WeekdaysEnum.Tuesday.value,
                                "value_ids": [(4, self.lead_times_by_day_value_2.id)],
                            },
                        ),
                    ]
                }
            )
        self.assertEqual(
            e.exception.args[0], "You can't have two lead time for the same day"
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date",
        return_value=None,
    )
    @freeze_time("2023-01-01")
    def test_run_buy_raise_error(self, mock_computed_date):
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        with self.assertRaises(ValidationError) as e:
            self.env["stock.rule"]._update_procurement(
                procurement,
                self.stock_rule,
            )
        mock_computed_date.assert_called_once()
        self.assertEqual(
            e.exception.args[0],
            "No delivery date found with the current configuration. "
            "Please check the supplier calendar, the warehouse calendar, "
            "the product expiration delay or adjust the event date.",
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date_working_days",
        return_value=None,
    )
    @freeze_time("2023-01-01")
    def test_run_buy_working_day_raise_error(self, mock_computed_date):
        self.stock_rule.is_delay_in_workable_days = True
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        with self.assertRaises(ValidationError) as e:
            self.env["stock.rule"]._update_procurement(
                procurement,
                self.stock_rule,
            )
        mock_computed_date.assert_called_once()
        self.assertEqual(
            e.exception.args[0],
            "No delivery date found with the current configuration. "
            "Please check the supplier calendar, the warehouse calendar, "
            "the product expiration delay or adjust the event date.",
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date",
        return_value={
            "expected_delivery_date": datetime(2025, 2, 1, 0, 0, 0),
            "actual_order_date": datetime(2025, 1, 1, 0, 0, 0),
        },
    )
    @freeze_time("2023-01-01")
    def test_run_buy(self, mock_computed_date):
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        self.env["stock.rule"]._update_procurement(
            procurement,
            self.stock_rule,
        )
        mock_computed_date.assert_called_once()
        self.assertEqual(
            procurement.values["date_planned"],  # noqa: PD011
            datetime(2025, 2, 1, 0, 0, 0),
        )

        self.assertEqual(
            procurement.values["date_order"]  # noqa: PD011
            .astimezone(pytz.timezone("Europe/Paris"))
            .strftime("%Y-%m-%d %H:%M:%S"),
            "2025-01-01 10:00:00",
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date_working_days",
        return_value={
            "expected_delivery_date": datetime(2025, 2, 1, 0, 0, 0),
            "actual_order_date": datetime(2025, 1, 1, 0, 0, 0),
        },
    )
    @freeze_time("2023-01-01")
    def test_run_buy_in_workable_day(self, mock_computed_date):
        self.stock_rule.is_delay_in_workable_days = True
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        self.env["stock.rule"]._update_procurement(
            procurement,
            self.stock_rule,
        )
        mock_computed_date.assert_called_once()
        self.assertEqual(
            procurement.values["date_planned"],  # noqa: PD011
            datetime(2025, 2, 1, 0, 0, 0),
        )

        self.assertEqual(
            procurement.values["date_order"]  # noqa: PD011
            .astimezone(pytz.timezone("Europe/Paris"))
            .strftime("%Y-%m-%d %H:%M:%S"),
            "2025-01-01 10:00:00",
        )

    @freeze_time("2023-01-01")
    def test_run_buy_without_planned_consumed_date_and_date_deadline(self):
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
            },
        )
        procurements = [(procurement, self.stock_rule)]
        procurements_copy = procurements.copy()
        self.env["stock.rule"]._update_procurement(procurement, self.stock_rule)
        self.assertEqual(
            procurements,
            procurements_copy,
        )
        self.assertEqual(
            procurement.values["date_planned"],  # noqa: PD011
            datetime(2024, 2, 1, 0, 0, 0),
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date",
        return_value={
            "expected_delivery_date": datetime(2025, 2, 1, 0, 0, 0),
            "actual_order_date": datetime(2025, 1, 1, 0, 0, 0),
        },
    )
    @freeze_time("2023-01-01")
    def test_run_buy_with_date_deadline(self, mock_computed_date):
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "date_deadline": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        self.env["stock.rule"]._update_procurement(
            procurement,
            self.stock_rule,
        )
        mock_computed_date.assert_called_once()
        self.assertEqual(
            procurement.values["date_planned"],  # noqa: PD011
            datetime(2025, 2, 1, 0, 0, 0),
        )

        self.assertEqual(
            procurement.values["date_order"]  # noqa: PD011
            .astimezone(pytz.timezone("Europe/Paris"))
            .strftime("%Y-%m-%d %H:%M:%S"),
            "2025-01-01 10:00:00",
        )

    @patch(
        "odoo.addons.stock_rule_delays_in_workable_days.models.resource_calendar."
        "ResourceCalendar.compute_order_dates_from_target_received_date",
        return_value={
            "expected_delivery_date": datetime(2025, 2, 1, 0, 0, 0),
            "actual_order_date": datetime(2025, 1, 1, 0, 0, 0),
        },
    )
    @freeze_time("2025-01-02")
    def test_run_buy_raise_error_if_date_in_past(self, mock_computed_date):
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "date_order": datetime(2024, 1, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        with self.assertRaises(ValidationError) as e:
            self.env["stock.rule"]._update_procurement(
                procurement,
                self.stock_rule,
            )
        self.assertEqual(
            e.exception.args[0],
            "The order date is in the past. Please check the supplier calendar, "
            "the warehouse calendar, the product expiration delay or adjust "
            "the event date.",
        )

    def test_run_buy_without_lead_time_by_ids(self):
        self.stock_rule.lead_times_by_day_ids = False
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            1,
            self.product_id.uom_id,
            self.stock_receipt_location,
            self.stock_rule,
            "ReallySpecificOrderName001",
            self.company_id,
            {
                "date_planned": datetime(2024, 2, 1, 0, 0, 0),
                "supplierinfo_id": self.product_id.seller_ids[0],
                "planned_consumed_date": datetime(2024, 2, 1, 0, 0, 0),
            },
        )
        self.env["stock.rule"]._update_procurement(
            procurement,
            self.stock_rule,
        )
        self.assertEqual(
            procurement.values["date_planned"],  # noqa: PD011
            datetime(2024, 2, 1, 0, 0, 0),
        )
