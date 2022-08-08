# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .common import TestShippingWeightCommon


class TestWeight(TestShippingWeightCommon):
    def test_move_weight(self):
        # 2 Box + 1 Small Box to satisfy 11 qties => 16kg
        self.assertEqual(self.move.weight, 16)

    def test_picking_weight_bulk(self):
        self.move.copy()
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            self.move.product_qty * 2,
        )
        picking = self.move.picking_id
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty
        self.assertEqual(self.move.picking_id.weight_bulk, 16 * 2)

    def test_picking_shipping_weight(self):
        # Add a Small Box of 1 unit without package
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            1,
        )
        # Add a Box of 5 units without package
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            5,
        )
        # Add a Box of 5 units within a package
        pack = self.env["stock.quant.package"].create({"name": "Test package"})
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            5,
            package_id=pack,
        )
        # The box of 5 items weights 7
        self.assertEqual(pack.shipping_weight, 7)
        # Reserve goods
        picking = self.move.picking_id
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty
        self.assertTrue(picking.package_ids)
        self.assertTrue(picking.move_ids_without_package)
        # Check shipping weight knowing there is no shipping weight on the package
        self.assertEqual(picking.shipping_weight, 16)
        pack.shipping_weight = 6
        picking.invalidate_cache(["shipping_weight"])
        self.assertEqual(picking.shipping_weight, 15)

    def test_package_weight(self):
        pack = self.env["stock.quant.package"].create({"name": "Test package"})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.wh.lot_stock_id, 7.0, package_id=pack
        )
        self.move._action_assign()
        # 1 Box + 2 Small Box to satisfy 7 qties => 11kg
        self.assertEqual(pack.weight, 11)
        # Shipping weight computed
        self.assertEqual(pack.shipping_weight, 11)
        # I can still override it
        pack.shipping_weight = 20
        self.assertEqual(pack.shipping_weight, 20)
