# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests.common import SavepointCase

from .common import CommonStockPurchaseOrderDateRule


class TestPurchaseOrderLine(CommonStockPurchaseOrderDateRule):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_id.expiration_time = 10

    @freeze_time("2024-02-01")
    def test_prepare_purchase_order_line_from_procurement(self):
        expected_date = datetime(2024, 2, 2, 0, 0, 0)
        res = self.env[
            "purchase.order.line"
        ]._prepare_purchase_order_line_from_procurement(
            product_id=self.product_id,
            product_qty=1,
            product_uom=self.product_id.uom_id,
            company_id=self.company_id,
            values={
                "supplier": self.product_id.seller_ids[0],
                "date_planned": expected_date,
            },
            po=self.purchase_order_id,
        )
        self.assertEqual(res["date_planned"], expected_date)
        self.assertEqual(
            res["planned_expiry_date"], expected_date + relativedelta(days=10)
        )

    def test_prepare_purchase_order_line_from_procurement_no_tracking(self):
        self.template_id.tracking = "none"
        res = self.env[
            "purchase.order.line"
        ]._prepare_purchase_order_line_from_procurement(
            product_id=self.product_id,
            product_qty=1,
            product_uom=self.product_id.uom_id,
            company_id=self.company_id,
            values={
                "supplier": self.product_id.seller_ids[0],
            },
            po=self.purchase_order_id,
        )
        self.assertNotIn("planned_expiry_date", res)

    def test_prepare_purchase_order_line_from_procurement_no_expiration_time(self):
        self.product_id.expiration_time = 0
        res = self.env[
            "purchase.order.line"
        ]._prepare_purchase_order_line_from_procurement(
            product_id=self.product_id,
            product_qty=1,
            product_uom=self.product_id.uom_id,
            company_id=self.company_id,
            values={
                "supplier": self.product_id.seller_ids[0],
            },
            po=self.purchase_order_id,
        )
        self.assertNotIn("planned_expiry_date", res)


class TestBeginningOfDay(SavepointCase):
    def test_date(self):
        res = self.env["purchase.order.line"]._beginning_of_day(
            datetime(2024, 2, 1, 12, 30, 0)
        )
        self.assertEqual(res, date(2024, 2, 1))

    def test_no_date(self):
        res = self.env["purchase.order.line"]._beginning_of_day(None)
        self.assertIsNone(res)
