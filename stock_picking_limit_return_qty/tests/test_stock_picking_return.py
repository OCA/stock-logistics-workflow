# Copyright 2023 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockReturnPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_return = cls.env["stock.return.picking"]
        cls.picking_return_line = cls.env["stock.return.picking.line"]
        cls.stock_move = cls.env["stock.move"]
        cls.product_product = cls.env["product.product"]

    @classmethod
    def _create_picking(cls, location, destination_location, picking_type):
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": destination_location.id,
            }
        )

    def test_00(self):
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        product_a = self.product_product.create(
            {"name": "Product A", "type": "product"}
        )
        product_b = self.product_product.create(
            {"name": "Product B", "type": "product"}
        )
        move_1 = self.stock_move.create(
            {
                "name": product_a.name,
                "product_id": product_a.id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        move_2 = self.stock_move.create(
            {
                "name": product_b.name,
                "product_id": product_b.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        move_2.quantity_done = 1
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        for line in return_wizard.product_return_moves:
            self.assertEqual(line.quantity, line.quantity_max)
            with self.assertRaises(ValidationError):
                line.quantity = line.quantity + 1
