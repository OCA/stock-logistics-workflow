from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockQuantPackageRestrictDisposableReuse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_obj = cls.env["stock.quant.package"]
        cls.stock_picking_obj = cls.env["stock.picking"]
        cls.stock_move_line_obj = cls.env["stock.move.line"]
        cls.stock_picking_type = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing")], limit=1
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product 1"})
        cls.product_2 = cls.env["product.product"].create({"name": "Test Product 2"})
        cls.package_type_1 = cls.env["stock.package.type"].create(
            {"name": "Test package Type 1", "restrict_reuse": True}
        )
        cls.package_type_2 = cls.env["stock.package.type"].create(
            {"name": "Test package Type 2", "restrict_reuse": False}
        )

    def create_package(self, name, package_use, package_type):
        return self.package_obj.create(
            {
                "name": name,
                "package_use": package_use,
                "package_type_id": package_type.id,
            }
        )

    def create_picking(self, product, package, qty=1):
        return self.stock_picking_obj.create(
            {
                "picking_type_id": self.stock_picking_type.id,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "qty_done": qty,
                            "result_package_id": package.id,
                        },
                    )
                ],
            }
        )

    def test_create_and_use_disposable_package(self):
        disposable_package = self.create_package(
            "Test Disposable Package", "disposable", self.package_type_1
        )
        self.create_picking(self.product, disposable_package)
        self.assertTrue(disposable_package.disposable_used)

    def test_reuse_disposable_package_with_restrict(self):
        disposable_package = self.create_package(
            "Test Disposable Package",
            "disposable",
            self.package_type_1,
        )
        self.create_picking(self.product, disposable_package)

        with self.assertRaisesRegex(
            ValidationError,
            "You can't reuse package %s because it is a disposable package that has "
            "already been used in a delivery." % disposable_package.name,
        ):
            self.create_picking(self.product_2, disposable_package)

    def test_reuse_disposable_package_without_restrict(self):
        disposable_package = self.create_package(
            "Test Disposable Package",
            "disposable",
            self.package_type_2,
        )
        first_picking = self.create_picking(self.product, disposable_package)
        second_picking = self.create_picking(self.product_2, disposable_package)
        self.assertTrue(second_picking.move_line_ids[0].result_package_id)
        self.assertEqual(
            first_picking.move_line_ids[0].result_package_id,
            second_picking.move_line_ids[0].result_package_id,
        )

    def test_reuse_non_disposable_package(self):
        non_disposable_package = self.create_package(
            "Test Non-Disposable Package", "reusable", self.package_type_1
        )
        picking = self.create_picking(self.product, non_disposable_package)

        second_picking = self.create_picking(self.product_2, non_disposable_package)

        self.assertTrue(second_picking.move_line_ids[0].result_package_id)
        self.assertEqual(
            picking.move_line_ids[0].result_package_id,
            second_picking.move_line_ids[0].result_package_id,
        )
