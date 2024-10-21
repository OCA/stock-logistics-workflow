# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from freezegun import freeze_time

from odoo import fields

from ..models.weekday import WeekdaysEnum
from .common import CommonStockPurchaseOrderDateRule
from .test_resource_calendar import attendance_ids


class TestPOFromProcurement(CommonStockPurchaseOrderDateRule):
    @classmethod
    def setUpClass(cls):
        """
        Setup case:

        P: Purchase Order date
        R: Receipt date
        N: Needs date

         TH | FR | SA | SU | MO | TU | WE | TH | FR | SA | SU
         --- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
         XX | XX |    |    | XX | xx | XX | XX | XX |    |     supplier calendar
         XX | XX | XX | XX | XX | xx | XX | XX | XX | XX | XX  warehouse calendar
         --- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
            | P  |    |    | RN |    |    |    |    |    |
            | P  |    |    |    | RN |    |    |    |    |
            | P  |    |    |    |    | RN |    |    |    |
            |    |    |    | P  |    |    | RN |    |    |
            |    |    |    |    | P  |    |    | RN |    |
            |    |    |    |    | P  |    |    | R  | N  |
            |    |    |    |    | P  |    |    | R  |    | N
        """
        super().setUpClass()
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        # only buy route is active, archive all existing buy rules
        cls.env["stock.location.route"].search(
            [("id", "!=", cls.buy_route.id)]
        ).active = False
        cls.buy_route.rule_ids.active = False
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.stock_loc.warehouse_id.calendar_id = False

        cls.partner_supplier.supplier_calendar_id = cls.env["resource.calendar"].create(
            {
                "name": "Supplier Calendar",
                "attendance_ids": attendance_ids(
                    WeekdaysEnum.Monday,
                    WeekdaysEnum.Tuesday,
                    WeekdaysEnum.Wednesday,
                    WeekdaysEnum.Thursday,
                    WeekdaysEnum.Friday,
                ),
            }
        )

        cls.lead_times_by_day_value_3 = cls.env["lead_times_by_day.value"].create(
            {"value": 3}
        )
        cls.lead_times_by_day_value_4 = cls.env["lead_times_by_day.value"].create(
            {"value": 4}
        )
        cls.lead_times_by_day_value_5 = cls.env["lead_times_by_day.value"].create(
            {"value": 5}
        )
        cls.stock_rule = cls.env["stock.rule"].create(
            {
                "name": "Test buy Rule",
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_id": cls.stock_loc.id,
                "action": "buy",
                "route_id": cls.buy_route.id,
                "company_id": cls.env.ref("base.main_company").id,
                "picking_type_id": cls.picking_type_in.id,
                "is_delay_in_workable_days": False,
                "delay": 0,
                "lead_times_by_day_ids": [
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Monday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Thursday (F+3), Friday (F+4), Saturday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Tuesday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Friday (F+3), Saturday (F+4), Sunday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Wednesday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Saturday (F+3), Sunday (F+4), Monday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Thursday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Sunday (F+3), Monday (F+4), Tuesday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Friday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Monday (F+3), Tuesday (F+4), Wednesday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Saturday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Tuesday (F+3), Wednesday (F+4), Thursday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Sunday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    (  # Wednesday (F+3), Thursday (F+4), Friday (F+5)
                                        cls.lead_times_by_day_value_3
                                        | cls.lead_times_by_day_value_4
                                        | cls.lead_times_by_day_value_5
                                    ).ids,
                                ),
                            ],
                        },
                    ),
                ],
            }
        )
        cls.product_id.route_ids |= cls.buy_route
        cls.product_id.expiration_time = 3

    @freeze_time("2024-02-29 08:00")
    def test_po_generation_1_po_with_two_po_lines(self):
        """
        P: Purchase Order date
        R: Receipt date
        N: Needs date

         TH | FR | SA | SU | MO | TU | WE
         29 | 01 | 02 | 03 | 04 | 05 | 06
         --- ---- ---- ---- ---- ---- ----
         XX | XX |    |    | XX | xx | XX  supplier calendar
         XX | XX | XX | XX | XX | xx | XX  warehouse calendar
         --- ---- ---- ---- ---- ---- ----
            | P  |    |    |    | RN |
            | P  |    |    |    |    | RN

        """

        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_id,
                    15,
                    self.product_id.uom_id,
                    self.stock_loc,
                    "a name",
                    "a product",
                    self.env.company,
                    {
                        # Tuesday
                        "date_planned": fields.Datetime.from_string("2024-03-05"),
                        "planned_consumed_date": fields.Datetime.from_string(
                            "2024-03-05"
                        ),
                        "supplierinfo_id": self.template_id.seller_ids[0],
                    },
                ),
            ]
        )
        # later an other procurement is running
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_id,
                    15,
                    self.product_id.uom_id,
                    self.stock_loc,
                    "a name",
                    "a product",
                    self.env.company,
                    {
                        # Wednesday
                        "date_planned": fields.Datetime.from_string("2024-03-06"),
                        "planned_consumed_date": fields.Datetime.from_string(
                            "2024-03-06"
                        ),
                        "supplierinfo_id": self.template_id.seller_ids[0],
                    },
                ),
            ]
        )

        po_lines = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product_id.id)]
        )
        self.assertEqual(len(po_lines.order_id), 1)
        self.assertEqual(
            len(po_lines),
            2,
            po_lines.mapped(lambda line: f"{line.date_planned} {line.product_qty}"),
        )
        # Tuesday
        self.assertEqual(
            len(
                po_lines.filtered(
                    lambda line: line.date_planned
                    == fields.Datetime.from_string("2024-03-05")
                )
            ),
            1,
        )
        # Wednesday
        self.assertEqual(
            len(
                po_lines.filtered(
                    lambda line: line.date_planned
                    == fields.Datetime.from_string("2024-03-06")
                )
            ),
            1,
        )
        # Friday
        self.assertEqual(po_lines.order_id.partner_id, self.partner_supplier)
        self.assertEqual(
            po_lines.order_id.date_order,
            fields.Datetime.from_string("2024-03-01 09:00"),
        )
