# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestProductCostPriceAvcoSyncLot(BaseCommon):
    """The module keeps one valuation chain per product, or one per lot for the
    products valuated by lot, and both kinds live in the same database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Test lot partner"})
        cls.categ = cls.env["product.category"].create(
            {
                "name": "AVCO by lot",
                "property_cost_method": "average",
                "property_valuation": "manual_periodic",
            }
        )

    def _create_product(self, name, lot_valuated=True):
        product = self.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
                "tracking": "lot" if lot_valuated else "none",
                "categ_id": self.categ.id,
                "standard_price": 0.0,
            }
        )
        if lot_valuated:
            product.product_tmpl_id.lot_valuated = True
        return product

    def _create_lot(self, product, name):
        return self.env["stock.lot"].create({"name": name, "product_id": product.id})

    def _do_picking(self, product, quantities, price=0.0, incoming=True):
        """quantities is a list of (lot, qty); lot may be an empty recordset."""
        total = sum(qty for _lot, qty in quantities)
        source = self.supplier_location if incoming else self.stock_location
        destination = self.stock_location if incoming else self.customer_location
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": (
                    self.picking_type_in if incoming else self.picking_type_out
                ).id,
                "partner_id": self.partner.id,
                "location_id": source.id,
                "location_dest_id": destination.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": total,
                            "product_uom": product.uom_id.id,
                            "location_id": source.id,
                            "location_dest_id": destination.id,
                            "price_unit": price,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids[:1]
        picking.move_line_ids.unlink()
        for lot, qty in quantities:
            self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "product_id": product.id,
                    "product_uom_id": move.product_uom.id,
                    "location_id": source.id,
                    "location_dest_id": destination.id,
                    "picking_id": picking.id,
                    "lot_id": lot.id if lot else False,
                    "quantity": qty,
                }
            )
        picking.move_line_ids.picked = True
        picking._action_done()
        return move

    def _layers(self, product, lot=None):
        domain = [("product_id", "=", product.id)]
        if lot is not None:
            domain.append(("lot_id", "=", lot.id if lot else False))
        return self.env["stock.valuation.layer"].search(domain, order="id")

    def _assert_product_cost_is_derived(self, product):
        """A product valuated by lot only summarises its lots, so its cost has
        to match what the layers say."""
        layers = self._layers(product)
        quantity = sum(layers.mapped("quantity"))
        value = sum(layers.mapped("value"))
        if quantity > 0:
            self.assertAlmostEqual(product.standard_price, value / quantity, 2)

    def test_cost_correction_stays_in_its_own_lot(self):
        """Correcting the cost of a lot re-prices that lot's outgoing layers and
        leaves every other lot alone.
        """
        product = self._create_product("lot cost correction")
        lot_a = self._create_lot(product, "LOT-A")
        lot_b = self._create_lot(product, "LOT-B")
        move_a = self._do_picking(product, [(lot_a, 10.0)], price=10.0)
        self._do_picking(product, [(lot_b, 10.0)], price=20.0)
        self._do_picking(product, [(lot_a, 4.0)], incoming=False)
        self._do_picking(product, [(lot_b, 5.0)], incoming=False)
        self.assertAlmostEqual(lot_a.standard_price, 10.0, 2)
        self.assertAlmostEqual(lot_b.standard_price, 20.0, 2)

        move_a.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        ).unit_cost = 12.0

        # The corrected lot follows, both in its cost and in what already left
        self.assertAlmostEqual(lot_a.standard_price, 12.0, 2)
        out_a = self._layers(product, lot_a).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(sum(out_a.mapped("unit_cost")), 12.0, 2)
        self.assertAlmostEqual(sum(out_a.mapped("value")), -48.0, 2)
        # The untouched lot keeps its own cost, it is not averaged with the other
        self.assertAlmostEqual(lot_b.standard_price, 20.0, 2)
        out_b = self._layers(product, lot_b).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(sum(out_b.mapped("value")), -100.0, 2)
        self._assert_product_cost_is_derived(product)

    def test_cost_correction_without_lot_valuation_still_averages(self):
        """The same correction on a product that is not valuated by lot keeps
        averaging over the whole product, as it always did.
        """
        product = self._create_product("no lot valuation", lot_valuated=False)
        empty_lot = self.env["stock.lot"]
        move_in = self._do_picking(product, [(empty_lot, 10.0)], price=10.0)
        self._do_picking(product, [(empty_lot, 10.0)], price=20.0)
        self._do_picking(product, [(empty_lot, 4.0)], incoming=False)
        self.assertAlmostEqual(product.standard_price, 15.0, 2)

        move_in.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        ).unit_cost = 12.0

        # (12 * 10 + 20 * 10) / 20
        self.assertAlmostEqual(product.standard_price, 16.0, 2)
        out_layer = self._layers(product).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(out_layer.unit_cost, 16.0, 2)

    def test_negative_lot_takes_the_real_incoming_cost(self):
        """A receipt into an oversold lot sets that lot's cost to the price
        actually paid, and leaves the other lots untouched.
        """
        product = self._create_product("negative lot")
        lot_a = self._create_lot(product, "LOT-A")
        lot_b = self._create_lot(product, "LOT-B")
        self._do_picking(product, [(lot_a, 10.0)], price=10.0)
        self._do_picking(product, [(lot_b, 10.0)], price=20.0)
        self._do_picking(product, [(lot_a, 20.0)], incoming=False)
        self.assertAlmostEqual(lot_a.quantity_svl, -10.0, 2)

        # Not enough to cover the deficit: the lot stays oversold
        self._do_picking(product, [(lot_a, 3.0)], price=30.0)

        self.assertAlmostEqual(lot_a.quantity_svl, -7.0, 2)
        self.assertAlmostEqual(lot_a.standard_price, 30.0, 2)
        self.assertAlmostEqual(lot_b.standard_price, 20.0, 2)

    def test_negative_lot_covered_lets_core_vacuum_work(self):
        """Once the deficit is covered, core's vacuum re-prices it and the
        module doesn't get in the way.
        """
        product = self._create_product("covered negative lot")
        lot = self._create_lot(product, "LOT-A")
        self._do_picking(product, [(lot, 10.0)], price=10.0)
        self._do_picking(product, [(lot, 20.0)], incoming=False)
        self._do_picking(product, [(lot, 15.0)], price=30.0)

        self.assertAlmostEqual(lot.quantity_svl, 5.0, 2)
        self.assertAlmostEqual(lot.value_svl, 150.0, 2)
        self.assertAlmostEqual(lot.standard_price, 30.0, 2)
        self._assert_product_cost_is_derived(product)

    def test_layers_before_enabling_lot_valuation_keep_their_own_chain(self):
        """Switching a product to valuation by lot leaves layers with no lot
        behind. They must keep replaying as the single chain they were, without
        mixing with the per lot ones.
        """
        product = self._create_product("switched to lot valuation", lot_valuated=False)
        product.product_tmpl_id.tracking = "lot"
        empty_lot = self.env["stock.lot"]
        lot_old = self._create_lot(product, "LOT-OLD")
        move_in = self._do_picking(product, [(lot_old, 10.0)], price=10.0)
        self._do_picking(product, [(lot_old, 4.0)], incoming=False)
        # While the product isn't valuated by lot, core writes no lot on the layers
        self.assertFalse(self._layers(product).lot_id)

        product.product_tmpl_id.lot_valuated = True
        lot = self._create_lot(product, "LOT-NEW")
        self._do_picking(product, [(lot, 10.0)], price=30.0)
        self.assertAlmostEqual(lot.standard_price, 30.0, 2)

        # Correcting a layer of the old chain must not touch the new lot
        move_in.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        ).unit_cost = 12.0

        self.assertAlmostEqual(lot.standard_price, 30.0, 2)
        old_out = self._layers(product, empty_lot).filtered(
            lambda svl: svl.quantity < 0 and svl.stock_move_id
        )
        self.assertAlmostEqual(sum(old_out.mapped("unit_cost")), 12.0, 2)

    def test_quantity_correction_restates_the_right_lot(self):
        """Correcting the received quantity of a done move restates the layer of
        that very lot, leaving the other lots alone, and keeps the remaining
        quantity Odoo needs for the vacuum in step with it.
        """
        product = self._create_product("quantity correction by lot")
        lot_a = self._create_lot(product, "LOT-A")
        lot_b = self._create_lot(product, "LOT-B")
        move_in = self._do_picking(product, [(lot_a, 10.0)], price=10.0)
        self._do_picking(product, [(lot_b, 10.0)], price=20.0)
        self._do_picking(product, [(lot_a, 4.0)], incoming=False)

        move_in.move_line_ids[:1].quantity = 12.0

        layer_a = self._layers(product, lot_a).filtered(lambda svl: svl.quantity > 0)
        self.assertEqual(len(layer_a), 1)
        self.assertAlmostEqual(layer_a.quantity, 12.0, 2)
        self.assertAlmostEqual(layer_a.value, 120.0, 2)
        # The remaining quantity follows the restatement: 12 received, 4 gone
        self.assertAlmostEqual(layer_a.remaining_qty, 8.0, 2)
        self.assertAlmostEqual(layer_a.remaining_value, 80.0, 2)
        self.assertAlmostEqual(lot_a.quantity_svl, 8.0, 2)
        # The other lot is untouched
        layer_b = self._layers(product, lot_b).filtered(lambda svl: svl.quantity > 0)
        self.assertAlmostEqual(layer_b.quantity, 10.0, 2)
        self.assertAlmostEqual(layer_b.remaining_qty, 10.0, 2)

    def test_a_manual_revaluation_survives_a_later_correction(self):
        """The stock revaluation wizard writes a layer that only carries value
        and names no target cost. Replaying the chain has to raise the running
        cost with it, the way a landed cost does, or the product ends up with a
        cost that contradicts what its own layers are worth.
        """
        product = self._create_product("revaluation then correction", False)
        empty = self.env["stock.lot"]
        move_in = self._do_picking(product, [(empty, 10.0)], price=10.0)
        self._do_picking(product, [(empty, 4.0)], incoming=False)
        wizard = self.env["stock.valuation.layer.revaluation"].create(
            {
                "product_id": product.id,
                "company_id": self.env.company.id,
                "added_value": 60.0,
                "account_journal_id": self.env["account.journal"]
                .search([("type", "=", "general")], limit=1)
                .id,
            }
        )
        wizard.action_validate_revaluation()
        self.assertAlmostEqual(product.standard_price, 20.0, 2)

        move_in.stock_valuation_layer_ids.filtered(
            lambda svl: not svl.stock_valuation_layer_id
        ).unit_cost = 12.0

        # 12 of purchase cost plus the 60 spread over the 6 units on hand
        self.assertAlmostEqual(product.standard_price, 22.0, 2)
        self.assertAlmostEqual(product.value_svl, 132.0, 2)
        self.assertAlmostEqual(
            product.standard_price, product.value_svl / product.quantity_svl, 2
        )

    def test_growing_a_delivery_takes_the_earlier_remainings(self):
        """Delivering more than what is on hand consumes what the earlier
        receipts had left and records the rest as the deficit the vacuum
        settles with the next one.
        """
        product = self._create_product("delivery grows", False)
        empty = self.env["stock.lot"]
        self._do_picking(product, [(empty, 10.0)], price=10.0)
        out_move = self._do_picking(product, [(empty, 8.0)], incoming=False)
        receipt = self._layers(product).filtered(lambda svl: svl.quantity > 0)
        self.assertAlmostEqual(receipt.remaining_qty, 2.0, 2)

        out_move.move_line_ids[:1].quantity = 15.0

        out_layer = self._layers(product).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(receipt.remaining_qty, 0.0, 2)
        self.assertAlmostEqual(out_layer.remaining_qty, -5.0, 2)

        # The next receipt settles it at the price really paid
        self._do_picking(product, [(empty, 10.0)], price=30.0)
        self.assertAlmostEqual(product.quantity_svl, 5.0, 2)
        self.assertAlmostEqual(product.value_svl, 150.0, 2)
        self.assertAlmostEqual(product.standard_price, 30.0, 2)

    def test_shrinking_a_receipt_below_what_left_records_the_deficit(self):
        """Correcting a receipt below what has already been delivered leaves the
        chain short. That has to be recorded where the vacuum looks for it, or
        the next receipt never re-prices those units.
        """
        product = self._create_product("receipt shrinks", False)
        empty = self.env["stock.lot"]
        in_move = self._do_picking(product, [(empty, 10.0)], price=10.0)
        self._do_picking(product, [(empty, 8.0)], incoming=False)

        in_move.move_line_ids[:1].quantity = 5.0

        receipt = self._layers(product).filtered(lambda svl: svl.quantity > 0)
        out_layer = self._layers(product).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(receipt.remaining_qty, 0.0, 2)
        # Three units had left that were never received
        self.assertAlmostEqual(out_layer.remaining_qty, -3.0, 2)
        self.assertAlmostEqual(product.quantity_svl, -3.0, 2)

        # The next receipt settles them at the price really paid
        self._do_picking(product, [(empty, 10.0)], price=30.0)
        self.assertAlmostEqual(product.quantity_svl, 7.0, 2)
        self.assertAlmostEqual(product.value_svl, 210.0, 2)
        self.assertAlmostEqual(product.standard_price, 30.0, 2)

    def test_force_sync_keeps_one_entry_point_per_lot(self):
        """Replaying a chain corrects everything after the starting point, so a
        selection of layers boils down to the oldest one of each lot.
        """
        product = self._create_product("forced resync by lot")
        lot_a = self._create_lot(product, "LOT-A")
        lot_b = self._create_lot(product, "LOT-B")
        self._do_picking(product, [(lot_a, 10.0)], price=10.0)
        self._do_picking(product, [(lot_b, 10.0)], price=20.0)
        self._do_picking(product, [(lot_a, 4.0)], incoming=False)
        self._do_picking(product, [(lot_b, 5.0)], incoming=False)
        layers = self._layers(product)

        entry_points = layers._filter_avco_sync_entry_points()

        # One per lot, and the oldest of each
        self.assertEqual(len(entry_points), 2)
        self.assertEqual(set(entry_points.mapped("lot_id")), {lot_a, lot_b})
        for lot in (lot_a, lot_b):
            oldest = self._layers(product, lot).sorted(lambda x: (x.create_date, x.id))[
                0
            ]
            self.assertIn(oldest, entry_points)
        # And running it changes nothing on an already coherent chain
        before = [(svl.unit_cost, svl.value) for svl in layers]
        layers.action_force_avco_sync()
        self.assertEqual([(svl.unit_cost, svl.value) for svl in layers], before)

    def test_force_sync_ignores_children_and_non_average(self):
        """Child layers have no chain of their own and standard cost products
        are none of this module's business.
        """
        product = self._create_product("forced resync, ignored layers")
        lot = self._create_lot(product, "LOT-A")
        self._do_picking(product, [(lot, 10.0)], price=10.0)
        child = self.env["stock.valuation.layer"].create(
            {
                "company_id": self.env.company.id,
                "product_id": product.id,
                "quantity": 0.0,
                "unit_cost": 0.0,
                "value": 5.0,
                "lot_id": lot.id,
                "stock_valuation_layer_id": self._layers(product)[0].id,
                "description": "a child layer",
            }
        )
        self.assertFalse(child._filter_avco_sync_entry_points())

    def test_valuation_as_of_a_past_date_comes_out_corrected(self):
        """A stock valuation asked for a date before the correction has to show
        the corrected figures. Companies that post the stock valuation
        periodically need the past to be right once the mistake is fixed, and
        Odoo's own correction layer, dated the day it is made, would not show up
        in that report.
        """
        product = self._create_product("grams instead of kilos")
        lot = self._create_lot(product, "LOT-A")
        # A thousand times the real quantity was received
        move_in = self._do_picking(product, [(lot, 1000.0)], price=10.0)
        layer = self._layers(product, lot)
        as_of = layer.create_date

        move_in.move_line_ids[:1].quantity = 1.0

        valued = product.with_context(to_date=as_of)
        self.assertAlmostEqual(valued.quantity_svl, 1.0, 2)
        self.assertAlmostEqual(valued.value_svl, 10.0, 2)

    def test_outgoing_layers_are_repriced_so_the_margin_follows(self):
        """The cost of what already left has to follow a quantity correction,
        because anything derived from it, such as the margin `sale_margin_sync`
        pushes to the sale order line, reads it from the outgoing layer. A wrong
        quantity skews the average against the other receipts, so correcting it
        moves the cost the outgoing moves were valued at.
        """
        product = self._create_product("margin follows the correction", False)
        empty_lot = self.env["stock.lot"]
        move_in = self._do_picking(product, [(empty_lot, 10.0)], price=10.0)
        self._do_picking(product, [(empty_lot, 10.0)], price=20.0)
        self._do_picking(product, [(empty_lot, 5.0)], incoming=False)
        out_layer = self._layers(product).filtered(lambda svl: svl.quantity < 0)
        self.assertAlmostEqual(out_layer.unit_cost, 15.0, 2)

        # Thirty units had really been received, not ten
        move_in.move_line_ids[:1].quantity = 30.0

        # (30 * 10 + 10 * 20) / 40
        self.assertAlmostEqual(out_layer.unit_cost, 12.5, 2)
        self.assertAlmostEqual(out_layer.value, -62.5, 2)
        self.assertAlmostEqual(product.standard_price, 12.5, 2)
