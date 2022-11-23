# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from time import sleep

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestProductCostPriceAvcoSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductCostPriceAvcoSync, cls).setUpClass()
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
                "type": "product",
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
                "move_lines": [
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
                "move_lines": [
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

    def _test_sync_cost_price(self):
        move_in = self.picking_in.move_lines[:1]
        move_in.product_uom_qty = 100
        move_in.price_unit = 5.0
        move_in.quantity_done = move_in.product_uom_qty
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
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.quantity_done = move_in_2.product_uom_qty
        picking_in_2._action_done()
        move_in_2.date = "2019-10-02 00:00:00"
        sleep(1)

        move_out = self.picking_out.move_lines[:1]
        move_out.quantity_done = move_out.product_uom_qty
        self.picking_out._action_done()
        move_out.date = "2019-10-03 00:00:00"

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_lines[:1]
        move_out_2.quantity_done = move_out_2.product_uom_qty
        picking_out_2._action_done()
        move_out_2.date = "2019-10-04 00:00:00"

        # Make an inventory
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Initial inventory",
                "filter": "partial",
                "location_id": self.warehouse.lot_stock_id.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                            "product_qty": 200,
                            "location_id": self.warehouse.lot_stock_id.id,
                        },
                    )
                ],
            }
        )
        inventory._action_done()
        inventory.move_ids.date = "2019-10-05 00:00:00"
        sleep(1)

        self.assertEqual(self.product.standard_price, 5.0)
        move_in.price_unit = 2.0
        self.assertEqual(self.product.standard_price, 2.27)
        self.assertAlmostEqual(move_out.price_unit, -2.27, 2)
        self.assertAlmostEqual(move_out_2.price_unit, -2.27, 2)

    def _test_sync_cost_price_and_history(self):
        company_id = self.picking_in.company_id.id
        move_in = self.picking_in.move_lines[:1]
        move_in.quantity_done = move_in.product_uom_qty
        self.picking_in._action_done()
        move_in.date = "2019-10-01 00:00:00"

        move_out = self.picking_out.move_lines[:1]
        move_out.quantity_done = move_out.product_uom_qty
        self.picking_out._action_done()
        move_out.date = "2019-10-01 01:00:00"

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.quantity_done = move_in_2.product_uom_qty
        picking_in_2._action_done()
        move_in_2.date = "2019-10-01 02:00:00"

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_lines[:1]
        move_out_2.product_uom_qty = 15
        move_out_2.quantity_done = move_out_2.product_uom_qty
        picking_out_2._action_done()
        move_out_2.date = "2019-10-01 03:00:00"

        picking_in_3 = self.picking_in.copy()
        move_in_3 = picking_in_3.move_lines[:1]
        move_in_3.quantity_done = move_in_3.product_uom_qty
        move_in_3.price_unit = 2.0
        picking_in_3._action_done()
        move_in_3.date = "2019-10-01 04:00:00"

        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        self.assertAlmostEqual(self.product.get_history_price(company_id), 2.0, 2)
        self.product.standard_price = 20.0
        self.assertAlmostEqual(self.product.get_history_price(company_id), 20.0, 2)

        move_in.price_unit = 10.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        self.assertAlmostEqual(move_out.price_unit, -10.0, 2)
        self.assertAlmostEqual(move_out_2.price_unit, -4.0, 2)
        self.assertAlmostEqual(
            self.product.get_history_price(
                company_id, move_in_3._previous_instant_date()
            ),
            4.0,
            2,
        )

        move_in_3.quantity_done = 5.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in_3.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 4.0, 2)

        (move_in | move_in_2 | move_in_3).write({"price_unit": 9.0})
        self.assertAlmostEqual(self.product.standard_price, 9.0, 2)

        svl_count = self.env["stock.valuation.layer"].search_count(
            [("company_id", "=", company_id), ("product_id", "=", self.product.id)]
        )
        self.assertEqual(svl_count, 4)  # TODO: Miralo que no se si es así

    def _test_sync_cost_price_multi_moves_done_at_same_time(self):
        move_in = self.picking_in.move_lines[:1]
        move_in.product_uom_qty = 10
        move_in.price_unit = 10.0
        move_in.quantity_done = move_in.product_uom_qty

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.price_unit = 5.0
        move_in_2.quantity_done = move_in_2.product_uom_qty

        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(6, 0, (self.picking_in + picking_in_2).ids)]}
        ).process()
        (self.picking_in + picking_in_2)._action_done()

        self.assertEqual(self.product.standard_price, 7.5)
        move_in_2.price_unit = 4.0
        self.assertEqual(self.product.standard_price, 7.0)
        move_in.price_unit = 8.0
        self.assertEqual(self.product.standard_price, 6)

        move_in.price_unit = 10.0
        self.assertEqual(self.product.standard_price, 7.0)
        move_in_2.price_unit = 5.0
        self.assertEqual(self.product.standard_price, 7.5)

    def _test_change_quantiy_price(self):
        """Write quantity and price to zero in a stock valuation layer"""
        self.picking_in.action_assign()
        move_in = self.picking_in.move_lines[:1]
        self.picking_in.move_line_ids.qty_done = move_in.product_uom_qty
        self.picking_in._action_done()

        picking_in_2 = self.picking_in.copy()
        picking_in_2.action_assign()
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.quantity_done = move_in_2.product_uom_qty
        picking_in_2._action_done()
        move_in_2.stock_valuation_layer_ids.unit_cost = 2.0
        self.assertAlmostEqual(self.product.standard_price, 1.5, 2)

        # Change qty before price
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 1.0, 2)
        move_in.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in.quantity_done = 10.0
        move_in.stock_valuation_layer_ids.unit_cost = 4.0
        self.assertAlmostEqual(self.product.standard_price, 3.0, 2)

        move_in.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in.quantity_done = 10.0
        move_in.stock_valuation_layer_ids.unit_cost = 1.0
        self.product.with_context(import_file=True).standard_price = 6.0
        svl_manual = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)], order="id DESC", limit=1
        )
        self.assertAlmostEqual(svl_manual.value, 90.0, 2)
        move_in.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(svl_manual.value, 100.0, 2)

    def create_picking(self, p_type="IN", qty=1.0, confirmed=True):
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
                    "move_lines": [
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
        if confirmed:
            picking.action_assign()
            move = picking.move_lines[:1]
            picking.move_line_ids.qty_done = move.product_uom_qty
            picking._action_done()
        return picking, move

    def _test_change_quantiy_price_xx(self):
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
        move_in_01.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in_01.quantity_done = 10.0
        move_in_01.stock_valuation_layer_ids.unit_cost = 4.0
        self.assertAlmostEqual(self.product.standard_price, 3.0, 2)

        move_in_01.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)

        move_in_01.quantity_done = 10.0
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
            "Before set move 1 unit cost to 2.0 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )

        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        self.print_svl(
            "After set move 1 unit cost to 2.0 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        self.assertAlmostEqual(move_in_01.stock_valuation_layer_ids.value, 20, 2)
        self.assertAlmostEqual(move_in_02.stock_valuation_layer_ids.value, 10, 2)
        self.assertAlmostEqual(move_out_01.stock_valuation_layer_ids.value, -7.5, 2)
        self.assertAlmostEqual(self.product.standard_price, 1.5, 2)

        # Case 2
        self.print_svl(
            "Before update inventory_quantity Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        quant.inventory_quantity = 6
        self.print_svl(
            "After set inventory_quantity to 6 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        picking_out_02, move_out_02 = self.create_picking("OUT", qty=10.0)
        self.print_svl(
            "After OUT 10 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        self.product.with_context(import_file=True).standard_price = 4.0
        self.print_svl(
            "After force standard price to 4 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        picking_in_03, move_in_03 = self.create_picking("IN", 2)
        self.print_svl(
            "After IN 2 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        self.product.with_context(import_file=True).standard_price = 7.0
        self.print_svl(
            "After force standard price to 7 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        picking_in_04, move_in_04 = self.create_picking("IN", 23)
        self.print_svl(
            "After IN 23 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        picking_out_03, move_out_03 = self.create_picking("OUT", 8)
        self.print_svl(
            "After OUT 8 Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        # Change qty before cost
        move_in_01.with_context(keep_avco_inventory=True).quantity_done = 0.0
        self.print_svl(
            "After force quantity to 0 in first IN move Quant:{} Cost:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.print_svl(
            "After force unit cost to 0 in first IN move Quant:{}".format(
                quant.quantity
            )
        )

        # Restore to initial values
        move_in_01.with_context(keep_avco_inventory=True).quantity_done = 10.0
        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        self.print_svl(
            "After restore initial values Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )

        # Change cost before quantity
        move_in_01.stock_valuation_layer_ids.unit_cost = 0.0
        self.print_svl(
            "After force unit cost to 0 in first IN move Quant:{}".format(
                quant.quantity
            )
        )
        move_in_01.quantity_done = 0.0
        self.print_svl(
            "After force quantity to 0 in first IN move Quant:{} Cost:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )

        # Restore to initial values
        move_in_01.stock_valuation_layer_ids.unit_cost = 2.0
        move_in_01.quantity_done = 10.0
        self.print_svl(
            "After restore initial values Quant:{} Standard Price:{}".format(
                quant.quantity, quant.product_id.standard_price
            )
        )

    def print_svl(self, char_info=""):
        msg_list = ["{}".format(char_info)]
        total_qty = total_value = 0.0
        for svl in self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)]
        ):
            total_qty += svl.quantity
            total_value += svl.value
            msg_list.append(
                "Qty:{:.3f} Cost:{:.3f} Value:{:.3f} RemQty:{:.3f}"
                " Totals: qty:{:.3f} val:{:.3f} avg:{:.3f} {}".format(
                    svl.quantity,
                    svl.unit_cost,
                    svl.value,
                    svl.remaining_qty,
                    total_qty,
                    total_value,
                    total_value / total_qty if total_qty else 0.0,
                    svl.description,
                )
            )
        msg_list.append(
            "Total qty: {:.3f} Total value: {:.3f} Cost average {:.3f}".format(
                total_qty, total_value, (total_value / total_qty if total_qty else 0.0)
            )
        )
        _logger.info("\n".join(msg_list))
