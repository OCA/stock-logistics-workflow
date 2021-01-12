# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import SavepointCase


class TestWeight(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestWeight, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.out_type_id.default_location_dest_id = cls.env.ref(
            "stock.stock_location_customers"
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "weight": 1,
                "packaging_ids": [
                    (0, 0, {"name": "Small Box", "qty": "1", "max_weight": "2"}),
                    (0, 0, {"name": "Box", "qty": "5", "max_weight": "7"}),
                ],
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "picking_type_id": cls.wh.out_type_id.id,
                "product_id": cls.product.id,
                "product_uom_qty": 11.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.wh.out_type_id.default_location_src_id.id,
                "location_dest_id": cls.wh.out_type_id.default_location_dest_id.id,
                "procure_method": "make_to_stock",
                "group_id": cls.env["procurement.group"].create({"name": "Test"}).id,
            }
        )
        cls.move._assign_picking()
        cls.move.picking_id.action_confirm()

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
            self.product, self.wh.out_type_id.default_location_src_id, 1,
        )
        # Add a Box of 5 units without package
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.wh.out_type_id.default_location_src_id, 5,
        )
        # Add a Box of 5 units within a package
        pack = self.env["stock.quant.package"].create({"name": "Test package"})
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            5,
            package_id=pack,
        )
        # Reserve goods
        picking = self.move.picking_id
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty
        self.assertTrue(picking.package_ids)
        self.assertTrue(picking.move_ids_without_package)
        # Check shipping weight knowing there is no shipping weight on the package
        self.assertEqual(picking.shipping_weight, 9)
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
