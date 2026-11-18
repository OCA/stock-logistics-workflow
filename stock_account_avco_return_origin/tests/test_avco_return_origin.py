# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAvcoReturnOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.avco_return_origin_cost = True
        cls.product_category = cls.env["product.category"].create(
            {"name": "AVCO Category", "property_cost_method": "average"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "AVCO Product",
                "type": "product",
                "categ_id": cls.product_category.id,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def _create_receipt(self, price_unit, qty=1):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Receipt",
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.product.uom_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_id": picking.id,
                "price_unit": price_unit,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.qty_done = qty
        picking.button_validate()
        return picking

    def _create_delivery(self, qty=1):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Delivery",
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_id": picking.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.qty_done = qty
        picking.button_validate()
        return picking

    def _prepare_return(self, picking, qty=1):
        """Create a supplier return and mark it done, but leave it unvalidated."""
        return_wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        ).save()
        return_wizard.product_return_moves.write({"quantity": qty})
        action = return_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        return_picking.move_ids.move_line_ids.qty_done = qty
        return return_picking

    def _create_return(self, picking, qty=1):
        return_picking = self._prepare_return(picking, qty=qty)
        return_picking.button_validate()
        return return_picking

    def _prepare_delivery(self, qty=1):
        """Create a customer delivery and mark it done, but leave it unvalidated."""
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Delivery",
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_id": picking.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.qty_done = qty
        return picking

    def test_avco_return_at_original_price(self):
        """Return reduces valuation at the original receipt price."""
        picking1 = self._create_receipt(100)
        self._create_receipt(150)
        self.assertEqual(self.product.standard_price, 125)  # AVCO
        self.assertEqual(self.product.value_svl, 250)

        return_picking = self._create_return(picking1)
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        self.assertEqual(return_svl.value, -100)
        self.assertEqual(return_svl.unit_cost, 100)

        # Remaining: 1 unit valued at 150, AVCO realigned to 150.
        self.assertEqual(self.product.quantity_svl, 1)
        self.assertEqual(self.product.value_svl, 150)
        self.assertEqual(self.product.standard_price, 150)

    def test_avco_return_disabled_uses_avco(self):
        """With the company setting off, the return behaves as standard AVCO."""
        self.env.company.avco_return_origin_cost = False
        picking1 = self._create_receipt(100)
        self._create_receipt(150)

        return_picking = self._create_return(picking1)
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        self.assertEqual(return_svl.value, -125)  # current AVCO
        self.assertEqual(self.product.value_svl, 125)
        self.assertEqual(self.product.standard_price, 125)

    def test_avco_return_partial(self):
        """Partial return uses the original receipt price pro-rata."""
        picking = self._create_receipt(100, qty=4)
        self._create_receipt(200, qty=4)
        self.assertEqual(self.product.standard_price, 150)  # (400 + 800) / 8

        self._create_return(picking, qty=2)
        # SVL value -200 (2 * 100), not -300 (2 * 150).
        self.assertEqual(self.product.quantity_svl, 6)
        self.assertEqual(self.product.value_svl, 1000)  # 1200 - 200
        self.assertAlmostEqual(self.product.standard_price, 166.67, places=2)

    def test_avco_return_depleting_stock_falls_back_to_avco(self):
        """A return that empties stock is valued at standard AVCO, not blocked."""
        picking1 = self._create_receipt(100)
        self._create_receipt(150)
        # Issue one unit at AVCO so the later return brings stock to zero.
        self._create_delivery(1)
        self.assertEqual(self.product.quantity_svl, 1)

        # Returning the original ¥100 unit would empty stock; rather than strand
        # value (or block), the return is valued at the standard average (125).
        return_picking = self._create_return(picking1)
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        self.assertEqual(return_svl.value, -125)
        self.assertEqual(self.product.quantity_svl, 0)
        self.assertEqual(self.product.value_svl, 0)

    def test_avco_return_capped_at_inventory_value(self):
        """A return is capped so the valuation never goes negative with stock on hand.

        With a large price gap between receipts, valuing the return at the
        original receipt price would remove more value than remains on hand.
        The removal is capped at the current inventory value, flooring the
        valuation at zero instead of driving it negative while stock is still
        on hand.
        """
        self._create_receipt(100, qty=2)
        receipt2 = self._create_receipt(1000, qty=1)
        self.assertEqual(self.product.quantity_svl, 3)
        self.assertEqual(self.product.value_svl, 1200)
        self.assertEqual(self.product.standard_price, 400)  # (200 + 1000) / 3

        # Deliver one unit at AVCO (400); 2 units / 800 remain.
        self._create_delivery(1)
        self.assertEqual(self.product.quantity_svl, 2)
        self.assertEqual(self.product.value_svl, 800)

        # Returning the ¥1000 unit at its origin price would remove 1000 from
        # an 800 valuation. Cap the removal at 800 so the valuation floors at 0.
        return_picking = self._create_return(receipt2)
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        self.assertEqual(return_svl.value, -800)
        self.assertEqual(return_svl.unit_cost, 800)
        self.assertEqual(self.product.quantity_svl, 1)
        self.assertEqual(self.product.value_svl, 0)
        self.assertEqual(self.product.standard_price, 0)

    def test_mixed_batch_delivery_valued_before_return_realign(self):
        """A delivery batched with a same-product return keeps the pre-return AVCO.

        Characterization test: when a single ``_action_done()`` values a normal
        delivery together with an origin-cost supplier return of the same product
        (e.g. multi-picking validation from the list view or a batch transfer),
        the delivery is valued at the average in effect before the return, and the
        standard_price realignment is applied only afterwards. See the comment in
        ``stock_move._create_out_svl``. This pins the intended behavior; do not
        "fix" it by reordering the split.
        """
        receipt1 = self._create_receipt(100, qty=2)
        self._create_receipt(150, qty=2)
        self.assertEqual(self.product.standard_price, 125)  # AVCO
        self.assertEqual(self.product.quantity_svl, 4)
        self.assertEqual(self.product.value_svl, 500)

        delivery = self._prepare_delivery(1)
        return_picking = self._prepare_return(receipt1, 1)

        # Validate both pickings in a single _action_done batch.
        (delivery | return_picking).button_validate()

        delivery_svl = delivery.move_ids.stock_valuation_layer_ids
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        # Delivery valued at the pre-return average (125), not the corrected one.
        self.assertEqual(delivery_svl.value, -125)
        self.assertEqual(delivery_svl.unit_cost, 125)
        # Return valued at the original receipt price (100).
        self.assertEqual(return_svl.value, -100)
        self.assertEqual(return_svl.unit_cost, 100)
        # Final: 2 units, 500 - 125 - 100 = 275, AVCO realigned to 137.5.
        self.assertEqual(self.product.quantity_svl, 2)
        self.assertEqual(self.product.value_svl, 275)
        self.assertEqual(self.product.standard_price, 137.5)

    def test_multiple_returns_emptying_stock_strands_no_value(self):
        """Several origin returns emptying stock in one batch leave value at 0.

        The standard_price is realigned after each origin return, so a later
        return whose quantity empties stock falls back to the correctly updated
        average instead of a stale one. Without per-move realignment the emptying
        return would strand valuation (qty 0 with value != 0).
        """
        receipt1 = self._create_receipt(100)
        receipt2 = self._create_receipt(150)
        self.assertEqual(self.product.quantity_svl, 2)
        self.assertEqual(self.product.value_svl, 250)

        return1 = self._prepare_return(receipt1, 1)
        return2 = self._prepare_return(receipt2, 1)
        # Validate both returns in a single _action_done batch; combined they
        # empty stock.
        (return1 | return2).button_validate()

        svl1 = return1.move_ids.stock_valuation_layer_ids
        svl2 = return2.move_ids.stock_valuation_layer_ids
        # First return at its origin price; the emptying return absorbs the
        # realigned residual so nothing is stranded.
        self.assertEqual(svl1.value, -100)
        self.assertEqual(svl2.value, -150)
        self.assertEqual(self.product.quantity_svl, 0)
        self.assertEqual(self.product.value_svl, 0)

    def test_fifo_return_unaffected(self):
        """FIFO returns must not be affected by the origin-price override.

        The company setting is on, but the product is FIFO, so
        ``_is_avco_origin_return`` must be False and this module must stay out of
        the way.
        """
        fifo_category = self.env["product.category"].create(
            {"name": "FIFO Category", "property_cost_method": "fifo"}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "FIFO Product",
                "type": "product",
                "categ_id": fifo_category.id,
            }
        )
        self._create_receipt(100)
        picking2 = self._create_receipt(150)
        self.assertFalse(picking2.move_ids._is_avco_origin_return())

    def test_standard_return_unaffected(self):
        """Standard-cost returns are valued at standard_price, not origin price."""
        standard_category = self.env["product.category"].create(
            {"name": "Standard Category", "property_cost_method": "standard"}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Standard Product",
                "type": "product",
                "categ_id": standard_category.id,
                "standard_price": 120,
            }
        )
        # Received at 100, but standard costing values it at standard_price (120).
        picking = self._create_receipt(100)
        self.assertFalse(picking.move_ids._is_avco_origin_return())
        self.assertEqual(self.product.value_svl, 120)

        return_picking = self._create_return(picking)
        return_svl = return_picking.move_ids.stock_valuation_layer_ids
        # Standard price (120), not the receipt's origin price (100).
        self.assertEqual(return_svl.value, -120)
        self.assertEqual(return_svl.unit_cost, 120)
        self.assertNotIn("original receipt price", return_svl.description or "")
        self.assertEqual(self.product.quantity_svl, 0)
        self.assertEqual(self.product.value_svl, 0)
