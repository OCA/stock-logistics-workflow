# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_valuation_layer_removal_date.hooks import fill_removal_date

EARLY = Datetime.to_datetime("2026-03-01 00:00:00")
LATE = Datetime.to_datetime("2026-09-01 00:00:00")
LATER = Datetime.to_datetime("2027-01-01 00:00:00")
LATEST = Datetime.to_datetime("2027-06-01 00:00:00")


class TestStockValuationLayerRemovalDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product = cls._create_product("Test Product")
        cls.valuated_product = cls._create_product(
            "Test Lot Valuated", lot_valuated=True
        )
        cls.lot_early = cls._create_lot("LOT-EARLY", EARLY)
        cls.lot_late = cls._create_lot("LOT-LATE", LATE)
        cls.lot_no_date = cls._create_lot("LOT-NO-DATE", False)

    @classmethod
    def _create_product(cls, name, lot_valuated=False):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
                "standard_price": 100.0,
                "lot_valuated": lot_valuated,
            }
        )

    @classmethod
    def _create_lot(cls, name, removal_date, product=None):
        lot = cls.env["stock.lot"].create(
            {"name": name, "product_id": (product or cls.product).id}
        )
        # removal_date is computed from the expiration date on creation, so it is
        # set afterwards to keep the test data predictable.
        lot.removal_date = removal_date
        return lot

    @classmethod
    def _create_move(cls, lots, product=None, outgoing=False, validate=False):
        """Create a move holding one unit of each lot, and optionally validate it."""
        product = product or cls.product
        source = cls.stock_location if outgoing else cls.supplier_location
        destination = cls.customer_location if outgoing else cls.stock_location
        move = cls.env["stock.move"].create(
            {
                "name": "Test move",
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": len(lots) or 1,
                "location_id": source.id,
                "location_dest_id": destination.id,
                "picking_type_id": (
                    cls.picking_type_out if outgoing else cls.picking_type_in
                ).id,
            }
        )
        cls._create_move_lines(move, lots)
        if validate:
            move.picked = True
            move._action_done()
        return move

    @classmethod
    def _create_move_lines(cls, move, lots):
        return cls.env["stock.move.line"].create(
            [
                {
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_id.uom_id.id,
                    "lot_id": lot.id,
                    "quantity": 1.0,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                }
                for lot in lots
            ]
        )

    @classmethod
    def _layer_vals(cls, move=False, lot=False):
        return {
            "product_id": cls.product.id,
            "company_id": cls.env.company.id,
            "quantity": 1.0,
            "value": 100.0,
            "unit_cost": 100.0,
            "stock_move_id": move.id if move else False,
            "lot_id": lot.id if lot else False,
        }

    @classmethod
    def _create_layer(cls, lots=None, lot=False):
        """Create a layer on a move holding `lots`, or on no move if it is None."""
        move = cls._create_move(lots) if lots is not None else False
        return cls.env["stock.valuation.layer"].create(cls._layer_vals(move, lot))

    def test_removal_date_of_a_new_layer(self):
        """A layer takes the earliest removal date among the lots of its move."""
        for lots, expected in [
            (self.lot_late, LATE),
            (self.lot_late | self.lot_early, EARLY),
            (self.lot_no_date | self.lot_late, LATE),  # dateless lots are ignored
            (self.env["stock.lot"], False),  # a move without any lot
            (None, False),  # a layer that is not tied to a move at all
        ]:
            with self.subTest(lots=lots):
                self.assertEqual(self._create_layer(lots).removal_date, expected)

    def test_removal_date_of_a_batch_of_layers(self):
        """Every layer of a create() batch gets the date of its own move."""
        early, late = self.env["stock.valuation.layer"].create(
            [
                self._layer_vals(self._create_move(lot))
                for lot in (self.lot_early, self.lot_late)
            ]
        )
        self.assertEqual(early.removal_date, EARLY)
        self.assertEqual(late.removal_date, LATE)

    def test_removal_date_of_a_validated_receipt(self):
        """The layers stock_account really makes get the date, not only fake ones."""
        move = self._create_move(self.lot_late | self.lot_early, validate=True)
        layer = move.stock_valuation_layer_ids
        self.assertEqual(len(layer), 1)
        self.assertFalse(layer.lot_id)
        self.assertEqual(layer.removal_date, EARLY)

    def test_removal_date_of_a_validated_delivery(self):
        self._create_move(self.lot_late, validate=True)
        move = self._create_move(self.lot_late, outgoing=True, validate=True)
        self.assertEqual(move.stock_valuation_layer_ids.removal_date, LATE)

    def test_removal_date_of_a_lot_valuated_product(self):
        """Such a product is valued per lot, so each layer carries its own lot."""
        product = self.valuated_product
        early = self._create_lot("LOT-VAL-EARLY", EARLY, product=product)
        late = self._create_lot("LOT-VAL-LATE", LATE, product=product)
        move = self._create_move(early | late, product=product, validate=True)
        layers = move.stock_valuation_layer_ids.grouped("lot_id")
        self.assertEqual(layers[early].removal_date, EARLY)
        self.assertEqual(layers[late].removal_date, LATE)

    def test_lot_removal_date_change_realigns_layers(self):
        layer = self._create_layer(self.lot_early | self.lot_late)
        # The late lot moves further away, the earliest one still drives the date.
        self.lot_late.removal_date = LATER
        self.assertEqual(layer.removal_date, EARLY)
        # The early lot moves past it, so the other lot becomes the earliest one.
        self.lot_early.removal_date = LATEST
        self.assertEqual(layer.removal_date, LATER)
        # Clearing the date of every lot of the move empties the layer as well.
        (self.lot_early | self.lot_late).removal_date = False
        self.assertFalse(layer.removal_date)

    def test_lot_removal_date_change_realigns_layers_of_a_lot(self):
        """A layer carrying a lot is realigned from that lot, not from its move."""
        layer = self._create_layer(self.lot_early | self.lot_late, lot=self.lot_late)
        self.lot_late.removal_date = LATER
        self.assertEqual(layer.removal_date, LATER)

    def test_expiration_date_change_realigns_layers(self):
        """removal_date also changes as a recompute of the product_expiry dates."""
        lot = self._create_lot("LOT-NO-EXPIRY", False)
        lot.write({"use_date": False, "alert_date": False})
        layer = self._create_layer(lot)
        self.assertFalse(layer.removal_date)
        lot.write({"expiration_date": LATEST})
        self.assertTrue(lot.removal_date, "product_expiry did not recompute the date")
        self.assertEqual(layer.removal_date, lot.removal_date)

    def test_move_lots_change_realigns_layers(self):
        """The lots of the move can change after the layer has been created."""
        move = self._create_move(self.lot_late)
        layer = self.env["stock.valuation.layer"].create(self._layer_vals(move))
        self.assertEqual(layer.removal_date, LATE)
        # An earlier lot is added to the move.
        self._create_move_lines(move, self.lot_early)
        self.assertEqual(layer.removal_date, EARLY)
        # The line of that lot ends up moving nothing, so its lot drops out of
        # stock.move.lot_ids even though the lots of the lines did not change.
        move.move_line_ids.filtered(lambda ml: ml.lot_id == self.lot_early).quantity = 0
        self.assertEqual(layer.removal_date, LATE)

    def test_done_move_line_quantity_correction_realigns_layers(self):
        """A done move line can still be corrected, which changes its move's lots."""
        move = self._create_move(self.lot_early | self.lot_late, validate=True)
        layer = move.stock_valuation_layer_ids
        self.assertEqual(layer.removal_date, EARLY)
        early_line = move.move_line_ids.filtered(lambda ml: ml.lot_id == self.lot_early)
        early_line.quantity = 0
        self.assertEqual(layer.removal_date, LATE)

    def test_fill_removal_date_hook(self):
        """The SQL of the install hook fills the same dates as the compute does."""
        move_layer = self._create_layer(self.lot_early | self.lot_late)
        lot_layer = self._create_layer(self.lot_late, lot=self.lot_late)
        empty_layer = self._create_layer(self.lot_no_date)
        layers = move_layer | lot_layer | empty_layer
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE stock_valuation_layer SET removal_date = NULL WHERE id IN %s",
            (tuple(layers.ids),),
        )
        self.env.invalidate_all()
        self.assertFalse(move_layer.removal_date)
        fill_removal_date(self.env.cr)
        self.env.invalidate_all()
        self.assertEqual(move_layer.removal_date, EARLY)
        self.assertEqual(lot_layer.removal_date, LATE)
        self.assertFalse(empty_layer.removal_date)
