# Copyright 2025 (APSL-Nagarro) - Miquel Alzanillas, Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestProductWeight(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env.ref("product.product_product_6")
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test",
                "uom_id": cls.env.ref("uom.product_uom_gram").id,
                "uom_po_id": cls.env.ref("uom.product_uom_gram").id,
                "detailed_type": "product",
            }
        )
        cls.product_template = cls.env.ref("product.product_product_7_product_template")
        cls.product_template2 = cls.env["product.template"].create(
            {
                "name": "Test",
                "uom_id": cls.env.ref("uom.product_uom_gram").id,
                "uom_po_id": cls.env.ref("uom.product_uom_gram").id,
                "detailed_type": "product",
            }
        )

    def test_stock_quant_total_weight(self):
        self.stock_quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 500,
                "location_id": self.env.ref("stock.stock_location_components").id,
            }
        )
        inventory_weight = self.stock_quant.quantity * self.product.product_weight
        self.assertEqual(self.stock_quant.inventory_weight, inventory_weight)
        self.stock_quant = self.env["stock.quant"].create(
            {
                "product_id": self.product2.id,
                "inventory_quantity": 500,
                "location_id": self.env.ref("stock.stock_location_components").id,
            }
        )
        inventory_weight = (
            self.stock_quant.quantity * self.product2.product_weight
        ) / self.product2.weight_uom_id.factor
        self.assertEqual(self.stock_quant.inventory_weight, inventory_weight)

    def test_stock_move_line_total_weight(self):
        self.move_id = self.env["stock.move"].create(
            {
                "name": "Test Stock Move",
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref(
                    "stock.location_refrigerator_small"
                ).id,
                "product_id": self.product.id,
                "picked": True,
                "product_uom_qty": 1,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 20,
                        },
                    )
                ],
            }
        )
        self.move_id._action_done()
        self.stock_move_line = self.move_id.move_line_ids[0]
        total_weight = (
            self.stock_move_line.quantity * self.product.product_weight
        ) / self.product.weight_uom_id.factor
        self.assertEqual(self.stock_move_line.total_weight, total_weight)

    def create_picking(self, quantity=0):
        picking_data = {
            "picking_type_id": self.env.ref("stock.picking_type_out").id,
            "move_type": "direct",
            "location_id": self.env.ref("stock.stock_location_stock").id,
            "location_dest_id": self.env.ref("stock.stock_location_components").id,
        }
        picking = self.env["stock.picking"].create(picking_data)

        move_data = {
            "picking_id": picking.id,
            "product_id": self.product.id,
            "location_id": self.env.ref("stock.stock_location_stock").id,
            "location_dest_id": self.env.ref("stock.stock_location_components").id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_deadline": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": self.product.name,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": quantity,
        }

        move = self.env["stock.move"].create(move_data)
        return picking, move

    def test_stock_move_total_weight(self):
        picking, move = self.create_picking(10.0)
        picking.button_validate()

        move._compute_total_weight()

        expected_weight = self.product.product_weight * move.product_uom_qty
        self.assertEqual(move.total_weight, expected_weight)
