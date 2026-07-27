# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from time import sleep

from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestProductCostPriceAvcoSync(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPicking = cls.env["stock.picking"]
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.categ_all = cls.env.ref("product.product_category_all")
        cls.categ_all.property_cost_method = "average"
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
                "standard_price": 1,
                "categ_id": cls.categ_all.id,
            }
        )
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.stock_location.id,
                        },
                    )
                ],
            }
        )

        cls.picking_out = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def test_sync_cost_price(self):
        move_in = self.picking_in.move_ids[:1]
        move_in.product_uom_qty = 100
        move_in.price_unit = 5.0
        move_in.quantity = move_in.product_uom_qty
        move_in.picked = True
        self.picking_in._action_done()
        move_in.date = "2019-10-01 00:00:00"
        # Why do we a sleep during 1 second after avery move validation?
        # The cost_price_avco_sync method remove future product price history
        # from 1 second before that the move date which has been upadated.
        # If we do not apply sleep for test all price history have the same
        # second so test crashes.
        # In a real scenario, the product price history are created with more
        # difference than 1 second.
        sleep(1)

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True
        picking_in_2._action_done()
        move_in_2.date = "2019-10-02 00:00:00"
        sleep(1)

        move_out = self.picking_out.move_ids[:1]
        move_out.quantity = move_out.product_uom_qty
        move_out.picked = True
        self.picking_out._action_done()
        move_out.date = "2019-10-03 00:00:00"

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_ids[:1]
        move_out_2.quantity = move_out_2.product_uom_qty
        move_out_2.picked = True
        picking_out_2._action_done()
        move_out_2.date = "2019-10-04 00:00:00"

        quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.warehouse.lot_stock_id.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        quant = quant.with_context(inventory_mode=True)
        quant.inventory_quantity = 200
        quant.action_apply_inventory()
        inventory_move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("is_inventory", "=", True)],
            order="id DESC",
            limit=1,
        )
        inventory_move.date = "2019-10-05 00:00:00"
        sleep(1)

        self.assertEqual(self.product.standard_price, 5.0)
        move_in.stock_valuation_layer_ids.unit_cost = 2.0
        self.assertEqual(self.product.standard_price, 2.27)
        self.assertAlmostEqual(move_out.stock_valuation_layer_ids.unit_cost, 2.27, 2)
        self.assertAlmostEqual(move_out_2.stock_valuation_layer_ids.unit_cost, 2.27, 2)

    def test_negative_stock_receipt_recomputes_clean_avco(self):
        """A receipt validated while on-hand quantity is negative must let
        the core negative-stock vacuum (`_run_fifo_vacuum`, which also
        applies to average costing, not just FIFO) re-price the deficit with
        the real incoming cost, instead of leaving the product with the
        runaway value that the raw weighted-average blend in
        `product_price_update_before_done` produces for a negative previous
        quantity.
        """
        move_in = self.picking_in.move_ids[:1]
        move_in.product_uom_qty = 10.0
        move_in.price_unit = 10.0
        move_in.quantity = move_in.product_uom_qty
        move_in.picked = True
        self.picking_in._action_done()
        self.assertEqual(self.product.standard_price, 10.0)

        # Send more than what is in stock: on-hand quantity goes negative.
        picking_out = self.picking_out.copy()
        move_out = picking_out.move_ids[:1]
        move_out.product_uom_qty = 20.0
        move_out.quantity = move_out.product_uom_qty
        move_out.picked = True
        picking_out._action_done()
        self.assertEqual(self.product.quantity_svl, -10.0)

        # Receive real stock at a different cost while still negative. The
        # naive blend would give (10 * -10 + 30 * 15) / 5 = 70, which is not
        # a purchase price that ever existed. The vacuum instead uses the 30
        # cost to fix the 10 units sent without real stock, leaving a clean
        # average.
        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.product_uom_qty = 15.0
        move_in_2.price_unit = 30.0
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True
        picking_in_2._action_done()

        self.assertEqual(self.product.quantity_svl, 5.0)
        self.assertEqual(self.product.value_svl, 150.0)
        self.assertEqual(self.product.standard_price, 30.0)

    def _oversell_and_receive_partially(self):
        """Receive 10 at 10, send 20, and receive back only 3 at 30, so the
        product is left oversold by 7 units. Returns the layer of the first
        receipt, which is the one to touch to trigger a full resync.
        """
        move_in = self.picking_in.move_ids[:1]
        move_in.product_uom_qty = 10.0
        move_in.price_unit = 10.0
        move_in.quantity = move_in.product_uom_qty
        move_in.picked = True
        self.picking_in._action_done()

        picking_out = self.picking_out.copy()
        move_out = picking_out.move_ids[:1]
        move_out.product_uom_qty = 20.0
        move_out.quantity = move_out.product_uom_qty
        move_out.picked = True
        picking_out._action_done()
        self.assertEqual(self.product.quantity_svl, -10.0)

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.product_uom_qty = 3.0
        move_in_2.price_unit = 30.0
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True
        picking_in_2._action_done()
        return move_in.stock_valuation_layer_ids

    def test_negative_stock_partial_receipt_keeps_real_cost(self):
        """A receipt that doesn't cover the whole deficit leaves the product
        oversold, and both of core's formulas then divide by that negative
        quantity: the blend in `product_price_update_before_done` would give
        (10 * -10 + 30 * 3) / -7 = 1.43, and the recompute closing
        `_run_fifo_vacuum` would give -70 / -7 = 10, the cost the deficit was
        booked at. The product has to keep the price actually paid instead.
        """
        self._oversell_and_receive_partially()
        self.assertEqual(self.product.quantity_svl, -7.0)
        self.assertEqual(self.product.value_svl, -70.0)
        self.assertEqual(self.product.standard_price, 30.0)

    def test_negative_stock_partial_receipt_survives_resync(self):
        """The cost of an oversold product must be the same whether it comes
        from validating the receipt or from replaying the whole layer history,
        so that editing any past move doesn't move the price around.
        """
        svl_in = self._oversell_and_receive_partially()
        self.assertEqual(self.product.standard_price, 30.0)
        # Rewrite the first receipt cost with its own value to force a full
        # AVCO resync over the whole chain without changing any figure.
        svl_in.unit_cost = 10.0
        self.assertEqual(self.product.quantity_svl, -7.0)
        self.assertEqual(self.product.standard_price, 30.0)

    def test_sync_cost_price_and_future_layers(self):
        move_in = self.picking_in.move_ids[:1]
        move_in.quantity = move_in.product_uom_qty
        move_in.picked = True
        self.picking_in._action_done()
        move_in.date = "2019-10-01 00:00:00"

        move_out = self.picking_out.move_ids[:1]
        move_out.quantity = move_out.product_uom_qty
        move_out.picked = True
        self.picking_out._action_done()
        move_out.date = "2019-10-01 01:00:00"

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True
        picking_in_2._action_done()
        move_in_2.date = "2019-10-01 02:00:00"

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_ids[:1]
        move_out_2.product_uom_qty = 15
        move_out_2.quantity = move_out_2.product_uom_qty
        move_out_2.picked = True
        picking_out_2._action_done()
        move_out_2.date = "2019-10-01 03:00:00"

        picking_in_3 = self.picking_in.copy()
        move_in_3 = picking_in_3.move_ids[:1]
        move_in_3.price_unit = 2.0
        move_in_3.quantity = move_in_3.product_uom_qty
        move_in_3.picked = True
        picking_in_3._action_done()
        move_in_3.date = "2019-10-01 04:00:00"

        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in.stock_valuation_layer_ids.unit_cost = 10.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        self.assertAlmostEqual(move_out.stock_valuation_layer_ids.unit_cost, 10.0, 2)
        self.assertAlmostEqual(move_out_2.stock_valuation_layer_ids.unit_cost, 4.0, 2)

        move_in_3.quantity = 5.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in_3.quantity = 0.0
        self.assertAlmostEqual(self.product.standard_price, 4.0, 2)

        (move_in | move_in_2 | move_in_3).stock_valuation_layer_ids.unit_cost = 9.0
        self.assertAlmostEqual(self.product.standard_price, 9.0, 2)

        svl_count = self.env["stock.valuation.layer"].search_count(
            [
                ("company_id", "=", self.picking_in.company_id.id),
                ("product_id", "=", self.product.id),
            ]
        )
        self.assertEqual(svl_count, 5)

    def test_sync_cost_price_multi_moves_done_at_same_time(self):
        move_in = self.picking_in.move_ids[:1]
        move_in.product_uom_qty = 10
        move_in.price_unit = 10.0
        move_in.quantity = move_in.product_uom_qty
        move_in.picked = True

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.price_unit = 5.0
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True

        (self.picking_in + picking_in_2)._action_done()

        self.assertEqual(self.product.standard_price, 7.5)
        move_in_2.stock_valuation_layer_ids.unit_cost = 4.0
        self.assertEqual(self.product.standard_price, 7.0)
        move_in.stock_valuation_layer_ids.unit_cost = 8.0
        self.assertEqual(self.product.standard_price, 6)

        move_in.stock_valuation_layer_ids.unit_cost = 10.0
        self.assertEqual(self.product.standard_price, 7.0)
        move_in_2.stock_valuation_layer_ids.unit_cost = 5.0
        self.assertEqual(self.product.standard_price, 7.5)

    def test_change_quantiy_price(self):
        """Write quantity and price to zero in a stock valuation layer"""
        self.picking_in.action_assign()
        move_in = self.picking_in.move_ids[:1]
        self.picking_in.move_line_ids.quantity = move_in.product_uom_qty
        self.picking_in.move_line_ids.picked = True
        self.picking_in._action_done()

        picking_in_2 = self.picking_in.copy()
        picking_in_2.action_assign()
        move_in_2 = picking_in_2.move_ids[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.quantity = move_in_2.product_uom_qty
        move_in_2.picked = True
        picking_in_2._action_done()
        move_in_2.stock_valuation_layer_ids.unit_cost = 2.0
        self.assertAlmostEqual(self.product.standard_price, 1.5, 2)

        # Change qty before price
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 1.0, 2)
        move_in.quantity = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in.move_line_ids.quantity = 10.0
        move_in.stock_valuation_layer_ids.unit_cost = 4.0
        self.assertAlmostEqual(self.product.standard_price, 3.0, 2)

        move_in.quantity = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in.move_line_ids.quantity = 10.0
        move_in.stock_valuation_layer_ids.unit_cost = 1.0
        self.product.with_context(import_file=True).standard_price = 6.0
        svl_manual = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)], order="id DESC", limit=1
        )
        self.assertAlmostEqual(svl_manual.value, 90.0, 2)
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(svl_manual.value, 100.0, 2)

    def create_picking(self, p_type="IN", qty=1.0, confirmed=True, price_unit=None):
        if p_type == "IN":
            picking_type = self.picking_type_in
            location_id = self.supplier_location
            location_dest_id = self.stock_location
        else:
            picking_type = self.picking_type_out
            location_id = self.stock_location
            location_dest_id = self.customer_location
        picking = (
            self.env["stock.picking"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "picking_type_id": picking_type.id,
                    "location_id": location_id.id,
                    "location_dest_id": location_dest_id.id,
                    "move_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "a move",
                                "product_id": self.product.id,
                                "product_uom_qty": qty,
                                "product_uom": self.product.uom_id.id,
                                "location_id": location_id.id,
                                "location_dest_id": location_dest_id.id,
                            },
                        )
                    ],
                }
            )
        )
        move = picking.move_ids[:1]
        if price_unit is not None:
            move.price_unit = price_unit
        if confirmed:
            picking.action_assign()
            picking.move_line_ids.quantity = move.product_uom_qty
            picking.move_line_ids.picked = True
            picking._action_done()
        return picking, move

    def test_sync_cost_price_with_negative_accumulated_qty(self):
        """An incoming move received while oversold sets the AVCO chain to its
        own cost: there are no units left to average against, and core's
        negative stock vacuum will settle the outstanding deficit with that very
        same cost once enough real stock arrives.
        """
        _picking_in, move_in = self.create_picking("IN", qty=10.0)
        _picking_out, move_out = self.create_picking("OUT", qty=10.0)
        move_out.move_line_ids.quantity = 20.0
        _picking_in_high_cost, move_in_high_cost = self.create_picking(
            "IN", qty=2.0, price_unit=100.0
        )

        self.assertAlmostEqual(self.product.quantity_svl, -8.0, 2)
        svl_in = move_in.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        )
        svl_out = move_out.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        )
        svl_in_high_cost = move_in_high_cost.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        )
        self.assertEqual(len(svl_in), 1)
        self.assertEqual(len(svl_out), 1)
        self.assertEqual(len(svl_in_high_cost), 1)
        self.assertAlmostEqual(svl_in.quantity, 10.0, 2)
        self.assertAlmostEqual(svl_out.quantity, -20.0, 2)
        self.assertAlmostEqual(svl_in_high_cost.quantity, 2.0, 2)

        svl_in.unit_cost = 2.0

        self.assertAlmostEqual(svl_in.value, 20.0, 2)
        self.assertAlmostEqual(svl_out.value, -40.0, 2)
        self.assertAlmostEqual(svl_in_high_cost.value, 200.0, 2)
        self.assertAlmostEqual(self.product.standard_price, 100.0, 2)

    def test_change_quantiy_price_with_inventory_adjustment(self):
        """Write quantity and price to zero in a stock valuation layer"""
        picking_in_01, move_in_01 = self.create_picking("IN", 10)
        quant = self.env["stock.quant"].search(
            [
                ("location_id.usage", "=", "internal"),
                ("product_id", "=", self.product.id),
            ]
        )
        picking_in_02, move_in_02 = self.create_picking("IN", 10)
        move_in_02.stock_valuation_layer_ids.unit_cost = 2.0
        self.assertAlmostEqual(self.product.standard_price, 1.5, 2)

        # Change qty before price
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 1.0, 2)
        move_in_01.quantity = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in_01.move_line_ids.quantity = 10.0
        move_in_01.stock_valuation_layer_ids.unit_cost = 4.0
        self.assertAlmostEqual(self.product.standard_price, 3.0, 2)

        move_in_01.quantity = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in_01.move_line_ids.quantity = 10.0
        move_in_01.stock_valuation_layer_ids.unit_cost = 1.0
        self.product.with_context(import_file=True).standard_price = 6.0
        svl_manual = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)], order="id DESC", limit=1
        )
        self.assertAlmostEqual(svl_manual.value, 90.0, 2)
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(svl_manual.value, 100.0, 2)

        # self.env.context.get('inventory_mode')
        quant = self.env["stock.quant"].search(
            [
                ("location_id.usage", "=", "internal"),
                ("product_id", "=", self.product.id),
            ]
        )
        quant.inventory_quantity = 0

        picking_out_01, move_out_01 = self.create_picking("OUT", qty=5.0)

    def test_change_quantiy_price_xx(self):
        """Write quantity and price to zero in a stock valuation layer"""
        # Case 1
        picking_in_01, move_in_01 = self.create_picking("IN", 10)
        picking_in_02, move_in_02 = self.create_picking("IN", 10)
        picking_out_01, move_out_01 = self.create_picking("OUT", qty=5.0)
        quant = (
            self.env["stock.quant"]
            .with_context(inventory_mode=True)
            .search(
                [
                    ("location_id.usage", "=", "internal"),
                    ("product_id", "=", self.product.id),
                ]
            )
        )

        self.print_svl(
            f"Before set move 1 unit cost to 2.0 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )

        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        self.print_svl(
            f"After set move 1 unit cost to 2.0 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        self.assertAlmostEqual(move_in_01.stock_valuation_layer_ids.value, 20, 2)
        self.assertAlmostEqual(move_in_02.stock_valuation_layer_ids.value, 10, 2)
        self.assertAlmostEqual(move_out_01.stock_valuation_layer_ids.value, -7.5, 2)
        self.assertAlmostEqual(self.product.standard_price, 1.5, 2)

        # Case 2
        self.print_svl(
            f"Before update inventory_quantity Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        quant.inventory_quantity = 6
        self.print_svl(
            f"After set inventory_quantity to 6 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        picking_out_02, move_out_02 = self.create_picking("OUT", qty=10.0)
        self.print_svl(
            f"After OUT 10 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        self.product.with_context(import_file=True).standard_price = 4.0
        self.print_svl(
            f"After force standard price to 4 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        picking_in_03, move_in_03 = self.create_picking("IN", 2)
        self.print_svl(
            f"After IN 2 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        self.product.with_context(import_file=True).standard_price = 7.0
        self.print_svl(
            f"After force standard price to 7 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        picking_in_04, move_in_04 = self.create_picking("IN", 23)
        self.print_svl(
            f"After IN 23 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        picking_out_03, move_out_03 = self.create_picking("OUT", 8)
        self.print_svl(
            f"After OUT 8 Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )
        # Change qty before cost
        move_in_01.with_context(keep_avco_inventory=True).quantity = 0.0
        move_in_01.with_context(keep_avco_inventory=True).picked = True
        self.print_svl(
            f"After force quantity to 0 in first IN move Quant:"
            f"{quant.quantity} Cost:{quant.product_id.standard_price}"
        )
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.print_svl(
            f"After force unit cost to 0 in first IN move Quant:" f"{quant.quantity}"
        )

        # Restore to initial values
        move_in_01.with_context(keep_avco_inventory=True).move_line_ids.quantity = 10.0
        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        self.print_svl(
            f"After restore initial values Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )

        # Change cost before quantity
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.print_svl(
            f"After force unit cost to 0 in first IN move Quant:" f"{quant.quantity}"
        )
        move_in_01.quantity = 0.0
        self.print_svl(
            f"After force quantity to 0 in first IN move Quant:{quant.quantity} "
            f"Cost:{quant.product_id.standard_price}"
        )

        # Restore to initial values
        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        move_in_01.move_line_ids.quantity = 10.0
        self.print_svl(
            f"After restore initial values Quant:{quant.quantity} "
            f"Standard Price:{quant.product_id.standard_price}"
        )

    def print_svl(self, char_info=""):
        msg_list = [f"{char_info}"]
        total_qty = total_value = 0.0
        for svl in self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)]
        ):
            total_qty += svl.quantity
            total_value += svl.value
            msg_list.append(
                f"Qty:{svl.quantity:.3f} Cost:{svl.unit_cost:.3f} "
                f"Value:{svl.value:.3f} RemQty:{svl.remaining_qty:.3f}"
                f" Totals: qty:{total_qty:.3f} val:{total_value:.3f} "
                f"avg:{total_value / total_qty if total_qty else 0.0:.3f} "
                f"{svl.description}"
            )
        msg_list.append(
            f"Total qty: {total_qty:.3f} Total value: {total_value:.3f} "
            f"Cost average {total_value / total_qty if total_qty else 0.0:.3f}"
        )
        _logger.info("\n".join(msg_list))
