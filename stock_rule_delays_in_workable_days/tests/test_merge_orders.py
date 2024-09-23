# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

from ..models.weekday import WeekdaysEnum


# TODO Not needed
class TestMergeOrders(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Orders from Monday to Friday have to be made the Friday before.
        An existing and sent purchase order can be updated with new lines to be
        delivered in at least 2 days.
        """
        super().setUpClass()
        # Enabling same day orders to be merged
        cls.env["ir.config_parameter"].sudo().set_param(
            "purchase_stock.delta_days_merge", 0
        )
        cls.env["stock.location.route"].search([]).active = False
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.stock_loc.warehouse_id.calendar_id = False

        cls.buy_route = cls.env["stock.location.route"].create(
            {
                "name": "Buy",
                "product_selectable": True,
                "active": True,
            }
        )

        # Lead times from Friday
        lead_times_by_day_values_ids = (
            # Next Monday
            cls.env["lead_times_by_day.value"].get_or_create_by_value(3)
            # Next Tuesday
            | cls.env["lead_times_by_day.value"].get_or_create_by_value(4)
            # Next Wednesday
            | cls.env["lead_times_by_day.value"].get_or_create_by_value(5)
            # Next Thursday
            | cls.env["lead_times_by_day.value"].get_or_create_by_value(6)
            # Next Friday
            | cls.env["lead_times_by_day.value"].get_or_create_by_value(7)
        ).ids

        cls.stock_rule = cls.env["stock.rule"].create(
            {
                "name": "Test buy Rule",
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_id": cls.stock_loc.id,
                "action": "buy",
                "route_id": cls.buy_route.id,
                "company_id": cls.env.company.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "is_delay_in_workable_days": False,
                "delay": 0,
                "lead_times_by_day_ids": [
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Friday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    lead_times_by_day_values_ids,
                                ),
                            ],
                        },
                    ),
                ],
            }
        )
        cls.supplier = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_3")
        cls.product.route_ids |= cls.buy_route
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )

        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                # A Friday
                "date_order": "2024-04-12",
                "state": "purchase",
            }
        )
        # Order for the Tuesday following the date order
        cls.purchase_order_line = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product.id,
                "product_qty": 1,
                "product_uom": cls.product.uom_id.id,
                "price_unit": 100,
                "date_planned": "2024-04-16",
            }
        )

    # Monday before the date order, product date planned is next Monday
    @freeze_time("2024-04-08 08:00")
    def test_can_update_future_order(self):
        # The Tuesday after
        date_planned = fields.Datetime.from_string("2024-04-15")
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            15,
            self.product.uom_id,
            self.stock_loc,
            "a name",
            "a product",
            self.env.company,
            {
                "date_planned": date_planned,
                "planned_consumed_date": date_planned,
                "supplierinfo_id": self.supplierinfo,
            },
        )
        self.env["procurement.group"].run([procurement])
        new_purchase_order_line = self.env["purchase.order.line"].search(
            [
                ("id", "!=", self.purchase_order_line.id),
                ("order_id", "=", self.purchase_order.id),
            ]
        )
        self.assertEqual(1, len(new_purchase_order_line))
        self.assertEqual(
            self.product,
            new_purchase_order_line.product_id,
        )
        self.assertEqual(
            15,
            new_purchase_order_line.product_qty,
        )
        self.assertEqual(
            date_planned,
            new_purchase_order_line.date_planned,
        )

    # Monday before the date order, product date planned is next Monday
    @freeze_time("2024-04-08 08:00")
    def test_update_line(self):
        # The Tuesday after
        date_planned_1 = fields.Datetime.from_string("2024-04-15")
        procurement_1 = self.env["procurement.group"].Procurement(
            self.product,
            15,
            self.product.uom_id,
            self.stock_loc,
            "a name",
            "a product",
            self.env.company,
            {
                "date_planned": date_planned_1,
                "planned_consumed_date": date_planned_1,
                "supplierinfo_id": self.supplierinfo,
            },
        )
        date_planned_2 = fields.Datetime.from_string("2024-04-15 12:00:00")
        procurement_2 = self.env["procurement.group"].Procurement(
            self.product,
            15,
            self.product.uom_id,
            self.stock_loc,
            "a name",
            "a product",
            self.env.company,
            {
                "date_planned": date_planned_2,
                "planned_consumed_date": date_planned_2,
                "supplierinfo_id": self.supplierinfo,
            },
        )
        self.env["procurement.group"].run([procurement_1, procurement_2])
        new_purchase_order_line = self.env["purchase.order.line"].search(
            [
                ("id", "!=", self.purchase_order_line.id),
                ("order_id", "=", self.purchase_order.id),
            ]
        )
        self.assertEqual(1, len(new_purchase_order_line))
        self.assertEqual(
            self.product,
            new_purchase_order_line.product_id,
        )
        self.assertEqual(
            30,
            new_purchase_order_line.product_qty,
        )
        self.assertEqual(
            date_planned_2,
            new_purchase_order_line.date_planned,
        )

    @freeze_time("2024-04-15 08:00")
    def test_order_in_the_past(self):
        # The Thursday after
        date_planned = fields.Datetime.from_string("2024-04-18")
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            15,
            self.product.uom_id,
            self.stock_loc,
            "a name",
            "a product",
            self.env.company,
            {
                # Tuesday
                "date_planned": date_planned,
                "planned_consumed_date": date_planned,
                "supplierinfo_id": self.supplierinfo,
            },
        )
        with self.assertRaisesRegex(
            ValidationError,
            "The order date is in the past. Please check the "
            "supplier calendar, the warehouse calendar, the product "
            "expiration delay or adjust the event date.",
        ):
            self.env["procurement.group"].run([procurement])
