# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPickingIncomingEmptyPackage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type_in.id,
                "location_id": cls.loc_customer.id,
                "location_dest_id": cls.loc_stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move 1a",
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 10,
                            "location_id": cls.loc_customer.id,
                            "location_dest_id": cls.loc_stock.id,
                        }
                    )
                ],
            }
        )

    def test_00(self):
        self.pick_type_in.empty_package_at_validation = True
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking._put_in_pack(self.picking.move_line_ids)
        self.picking._action_done()

        quant = self.product.stock_quant_ids.filtered(
            lambda q, loc=self.loc_stock: q.location_id == loc
        )
        self.assertEqual(len(quant), 1)
        self.assertTrue(quant.package_id)

    def test_01(self):
        self.pick_type_in.empty_package_at_validation = True
        package = self.env["stock.quant.package"].create({"name": "Pack A"})
        self.picking.move_line_ids.write(
            {"package_id": package.id, "result_package_id": package.id}
        )
        self.picking.action_confirm()
        self.picking.action_set_quantities_to_reservation()
        self.picking._action_done()

        quant = self.product.stock_quant_ids.filtered(
            lambda q, loc=self.loc_stock: q.location_id == loc
        )
        self.assertEqual(len(quant), 1)
        self.assertFalse(quant.package_id)

    def test_02(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking._put_in_pack(self.picking.move_line_ids)
        self.picking._action_done()

        quant = self.product.stock_quant_ids.filtered(
            lambda q, loc=self.loc_stock: q.location_id == loc
        )
        self.assertEqual(len(quant), 1)
        self.assertTrue(quant.package_id)
