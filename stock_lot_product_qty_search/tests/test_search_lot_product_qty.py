# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests import TransactionCase
from odoo.tools import float_compare, float_is_zero


class TestSearchLotProductQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_precision = cls.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        cls.existing_lots_qties = (
            cls.env["stock.production.lot"]
            .search([])
            .read(["product_id", "product_qty"])
        )

    def test_search_with_product_qty(self):
        lots_with_qties = self.env["stock.production.lot"].search(
            [("product_qty", ">", 0)]
        )
        self.assertEqual(
            lots_with_qties.ids,
            [
                exist_lot["id"]
                for exist_lot in self.existing_lots_qties
                if float_compare(
                    exist_lot["product_qty"], 0, precision_digits=self.uom_precision
                )
                > 0
            ],
        )

    def test_search_without_product_qty(self):
        lots_with_qties = self.env["stock.production.lot"].search(
            [("product_qty", "=", 0)]
        )
        self.assertEqual(
            lots_with_qties.ids,
            [
                exist_lot["id"]
                for exist_lot in self.existing_lots_qties
                if float_is_zero(
                    exist_lot["product_qty"], precision_digits=self.uom_precision
                )
            ],
        )

    def test_search_bigger_product_qty(self):
        lots_with_qties = self.env["stock.production.lot"].search(
            [("product_qty", ">", 50)]
        )
        self.assertEqual(
            lots_with_qties.ids,
            [
                exist_lot["id"]
                for exist_lot in self.existing_lots_qties
                if float_compare(
                    exist_lot["product_qty"], 50, precision_digits=self.uom_precision
                )
                > 0
            ],
        )

    def test_search_smaller_product_qty(self):
        lots_with_qties = self.env["stock.production.lot"].search(
            [("product_qty", "<", 1)]
        )
        self.assertEqual(
            lots_with_qties.ids,
            [
                exist_lot["id"]
                for exist_lot in self.existing_lots_qties
                if float_compare(
                    exist_lot["product_qty"], 1, precision_digits=self.uom_precision
                )
                < 0
            ],
        )

    def test_search_product_qty_args(self):
        with self.assertRaises(UserError):
            self.env["stock.production.lot"].search([("product_qty", "like", 1)])
        with self.assertRaises(UserError):
            self.env["stock.production.lot"].search([("product_qty", "=", "1")])
