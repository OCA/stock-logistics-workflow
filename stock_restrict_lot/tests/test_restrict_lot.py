from odoo.tests.common import TransactionCase


class TestRestrictLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.product.write({"tracking": "lot"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )

    def test_00_move_restrict_lot_propagation(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.output_loc.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "route_ids": [(6, 0, self.warehouse.delivery_route_id.ids)],
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        orig_move = move.move_orig_ids
        self.assertEqual(orig_move.restrict_lot_id.id, self.lot.id)

    def test_01_move_split_and_copy(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.output_loc.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 2,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "route_ids": [(6, 0, self.warehouse.delivery_route_id.ids)],
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        vals_list = move._split(1)
        new_move = self.env["stock.move"].create(vals_list)
        self.assertEqual(new_move.restrict_lot_id.id, move.restrict_lot_id.id)
        other_move = move.copy()
        self.assertFalse(other_move.restrict_lot_id.id)

    def _update_product_stock(self, qty, lot_id=False):
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "lot_id": lot_id,
                "inventory_quantity": qty,
            }
        )
        quant.action_apply_inventory()

    def test_02_move_restrict_lot_reservation(self):
        lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "product_id": self.product.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        self._update_product_stock(1, lot2.id)

        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        # move should not reserve wrong free lot
        self.assertEqual(move.state, "confirmed")

        self._update_product_stock(1, self.lot.id)
        move._action_assign()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.move_line_ids.lot_id.id, self.lot.id)
