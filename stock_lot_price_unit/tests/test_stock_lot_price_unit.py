# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.common import TestStockCommon


class TestStockLotPriceUnit(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Product created in TestStockCommon
        cls.productA.tracking = "lot"

        # Create Lot
        cls.lot = cls.env["stock.lot"].create(
            {
                "product_id": cls.productA.id,
                "company_id": cls.env.user.company_id.id,
                "name": "LOT001",
            }
        )

    def create_picking(self):
        return self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location,
                "location_dest_id": self.stock_location,
                "picking_type_id": self.picking_type_in,
            }
        )

    def create_stock_move(self, picking, product, price):
        return self.env["stock.move"].create(
            {
                "name": "Move product to stock",
                "product_id": product.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 5.0,
                "picking_id": picking.id,
                "price_unit": price,
            }
        )

    def create_stock_move_line(self, move, lot):
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_uom_id": move.product_uom.id,
                "qty_done": move.product_uom_qty,
                "lot_id": lot.id,
            }
        )

    def test_stock_lot_price_unit(self):
        picking = self.create_picking()
        move = self.create_stock_move(picking, self.productA, 1000)
        self.create_stock_move_line(move, self.lot)

        picking.action_confirm()
        picking.action_assign()
        picking._action_done()
        # Check if the lot's price_unit equals the move's price_unit
        self.assertEqual(move.price_unit, self.lot.price_unit)

        quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_location),
                ("product_id", "=", self.productA.id),
            ],
            limit=1,
        )
        self.assertEqual(quant.price_unit, self.lot.price_unit)

        picking = self.create_picking()
        move = self.create_stock_move(picking, self.productA, 1500)
        self.create_stock_move_line(move, self.lot)

        picking.action_confirm()
        picking.action_assign()
        picking._action_done()

        # Check if the lot's price_unit is not changed
        self.assertEqual(self.lot.price_unit, 1000.00)
