# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo.tests import common


class TestProductLotWarranty(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company1 = cls.env["res.company"].create({"name": "Test company1"})
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "TestProduct",
                "warranty_type": "day",
                "warranty": 5,
            }
        )

    def test_productlot_warranty(self):
        production_lot = self.env["stock.lot"].create(
            {"product_id": self.product1.id, "company_id": self.company1.id}
        )
        production_lot._onchange_product_id()
        self.assertEqual(
            production_lot.warranty_exp_date,
            (datetime.now() + timedelta(days=5)).date(),
        )

    def test_productlot_no_product(self):
        # s.p.lot "product_id" is required=True
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env["stock.lot"].create(
                {"product_id": False, "company_id": self.company1.id}
            )

    def test_productlot_no_warranty_type(self):
        # product.template "warranty_type" is required=True
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env["product.product"].create(
                {
                    "name": "TestProduct",
                    "warranty_type": False,
                    "warranty": 5,
                }
            )

    def test_productlot_no_warranty(self):
        product2 = self.env["product.product"].create(
            {
                "name": "TestProduct",
                "warranty_type": "week",
                "warranty": 0,
            }
        )
        production_lot = self.env["stock.lot"].create(
            {"product_id": product2.id, "company_id": self.company1.id}
        )
        production_lot._onchange_product_id()
        self.assertFalse(production_lot.warranty_exp_date)

    def test_get_warranty_exp_date(self):
        production_lot = self.env["stock.lot"].create(
            {"product_id": self.product1.id, "company_id": self.company1.id}
        )
        timestamp = datetime.now() - timedelta(days=3)
        self.assertEqual(
            production_lot._get_warranty_exp_date(),
            (datetime.now() + timedelta(days=5)).date(),
        )
        self.assertEqual(
            production_lot._get_warranty_exp_date(timestamp),
            (datetime.now() + timedelta(days=2)).date(),
        )
        self.assertEqual(
            production_lot._get_warranty_exp_date(timestamp.date()),
            (datetime.now() + timedelta(days=2)).date(),
        )
