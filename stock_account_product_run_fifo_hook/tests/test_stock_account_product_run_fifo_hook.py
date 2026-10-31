# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import TransactionCase


class TestStockAccountProductRunFifoHook(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_g = cls.env.ref("uom.product_uom_gram")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product in kg",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": cls.env.ref("uom.product_uom_kgm").id,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def _validate_picking(self, picking_type, location, location_dest, qty):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.uom_g.id,
                            "product_uom_qty": qty,
                            "quantity": qty,
                            "location_id": location.id,
                            "location_dest_id": location_dest.id,
                        }
                    )
                ],
            }
        )
        picking.button_validate()
        return picking

    def test_valuation_rounding_method(self):
        """The delivered quantity is rounded like the received one (HALF-UP)"""
        receipt = self._validate_picking(
            self.env.ref("stock.picking_type_in"),
            self.env.ref("stock.stock_location_suppliers"),
            self.stock_location,
            11,
        )
        self.assertEqual(receipt.move_ids.stock_valuation_layer_ids.quantity, 0.01)
        delivery = self._validate_picking(
            self.env.ref("stock.picking_type_out"),
            self.stock_location,
            self.env.ref("stock.stock_location_customers"),
            11,
        )
        self.assertEqual(delivery.move_ids.product_qty, 0.01)
        self.assertEqual(delivery.move_ids.stock_valuation_layer_ids.quantity, -0.01)
        self.assertEqual(self.product.qty_available, 0.0)
        self.assertEqual(self.product.quantity_svl, 0.0)
