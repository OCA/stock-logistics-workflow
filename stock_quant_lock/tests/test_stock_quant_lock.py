# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools.float_utils import float_compare


class TestStockQuantLock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test lock product",
                "detailed_type": "product",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "LOCK-LOT-001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.lock_picking_type = cls.env.ref("stock.picking_type_internal")
        cls.lock_picking_type.write(
            {
                "allow_quant_lock": True,
                "reservation_method": "manual",
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": cls.output_location.id,
            }
        )

        cls.out_picking_type = cls.env.ref("stock.picking_type_out")
        cls.out_picking_type.reservation_method = "manual"

    def _create_move(self, picking, product, qty, src, dest):
        return self.env["stock.move"].create(
            {
                "name": product.display_name,
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "company_id": self.env.company.id,
            }
        )

    def _get_exact_quant(self, product, location, lot=False):
        quants = self.env["stock.quant"]._gather(
            product,
            location,
            lot_id=lot,
            strict=True,
        )
        if lot:
            quants = quants.filtered(lambda q: q.lot_id == lot)
        else:
            quants = quants.filtered(lambda q: not q.lot_id)
        return quants[:1]

    def _prepare_quant_with_partial_reservation(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 10.0, lot_id=self.lot
        )
        quant = self._get_exact_quant(self.product, self.stock_location, lot=self.lot)
        self.assertEqual(len(quant), 1)

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.out_picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "company_id": self.env.company.id,
            }
        )
        move = self._create_move(
            picking,
            self.product,
            4.0,
            self.stock_location,
            self.customer_location,
        )
        move._action_confirm()
        move._action_assign()

        self.assertEqual(
            float_compare(
                move.reserved_availability,
                4.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        self.assertEqual(
            float_compare(
                quant.reserved_quantity,
                4.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        self.assertEqual(
            float_compare(
                quant.available_quantity,
                6.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        return quant

    def test_lock_reserves_only_unreserved_quantity(self):
        quant = self._prepare_quant_with_partial_reservation()

        wizard = (
            self.env["stock.quant.lock.wizard"]
            .with_context(
                active_model="stock.quant",
                active_ids=quant.ids,
            )
            .create(
                {
                    "picking_type_id": self.lock_picking_type.id,
                }
            )
        )
        wizard.action_lock()

        self.assertTrue(quant.is_locked_by_picking)
        self.assertEqual(quant.lock_move_count, 1)
        self.assertEqual(
            float_compare(
                quant.reserved_quantity,
                10.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        self.assertEqual(
            float_compare(
                quant.available_quantity,
                0.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        action = quant.action_view_lock_moves()
        self.assertEqual(action["res_model"], "stock.move")
        self.assertEqual(action["domain"], [("quant_lock_quant_id", "=", quant.id)])

    def test_lock_targets_selected_quant(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 10.0
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 5.0, lot_id=self.lot
        )

        target_quant = self._get_exact_quant(
            self.product,
            self.stock_location,
            lot=self.lot,
        )
        other_quant = self._get_exact_quant(self.product, self.stock_location)
        self.assertEqual(len(target_quant), 1)
        self.assertEqual(len(other_quant), 1)

        target_quant._lock_with_picking_type(self.lock_picking_type)

        self.assertTrue(target_quant.is_locked_by_picking)
        self.assertFalse(other_quant.is_locked_by_picking)
        self.assertEqual(
            float_compare(
                target_quant.reserved_quantity,
                5.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        self.assertEqual(
            float_compare(
                other_quant.reserved_quantity,
                0.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )

    def test_unlock_cancels_lock_move_and_releases_reservation(self):
        quant = self._prepare_quant_with_partial_reservation()
        quant._lock_with_picking_type(self.lock_picking_type)

        lock_move = self.env["stock.move"].search(
            [("quant_lock_quant_id", "=", quant.id)], limit=1
        )
        self.assertEqual(lock_move.state, "assigned")

        quant.action_unlock_quant()

        self.assertFalse(quant.is_locked_by_picking)
        self.assertEqual(lock_move.state, "cancel")
        self.assertEqual(
            float_compare(
                quant.reserved_quantity,
                4.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
        self.assertEqual(
            float_compare(
                quant.available_quantity,
                6.0,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )

    def test_unlock_done_lock_move_raises(self):
        quant = self._prepare_quant_with_partial_reservation()
        quant._lock_with_picking_type(self.lock_picking_type)
        lock_move = self.env["stock.move"].search(
            [("quant_lock_quant_id", "=", quant.id)], limit=1
        )

        lock_move.quantity_done = lock_move.product_uom_qty
        lock_move._action_done()

        with self.assertRaises(UserError):
            quant.action_unlock_quant()

    def test_lock_action_reserves_for_all_reservation_modes(self):
        for mode in ("manual", "at_confirm", "by_date"):
            self.lock_picking_type.reservation_method = mode
            lot = self.env["stock.lot"].create(
                {
                    "name": "LOCK-MODE-%s" % mode,
                    "product_id": self.product.id,
                    "company_id": self.env.company.id,
                }
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product,
                self.stock_location,
                3.0,
                lot_id=lot,
            )
            quant = self._get_exact_quant(self.product, self.stock_location, lot=lot)

            wizard = (
                self.env["stock.quant.lock.wizard"]
                .with_context(
                    active_model="stock.quant",
                    active_ids=quant.ids,
                )
                .create(
                    {
                        "picking_type_id": self.lock_picking_type.id,
                    }
                )
            )
            wizard.action_lock()

            self.assertTrue(quant.is_locked_by_picking)
            self.assertEqual(
                float_compare(
                    quant.available_quantity,
                    0.0,
                    precision_rounding=self.product.uom_id.rounding,
                ),
                0,
            )
            quant.action_unlock_quant()

    def test_batch_lock_and_unlock_for_selected_quants(self):
        lot2 = self.env["stock.lot"].create(
            {
                "name": "LOCK-LOT-BATCH-002",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.stock_location,
            2.0,
            lot_id=self.lot,
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.stock_location,
            3.0,
            lot_id=lot2,
        )

        quant_1 = self._get_exact_quant(self.product, self.stock_location, lot=self.lot)
        quant_2 = self._get_exact_quant(self.product, self.stock_location, lot=lot2)
        self.assertEqual(len(quant_1), 1)
        self.assertEqual(len(quant_2), 1)

        wizard = (
            self.env["stock.quant.lock.wizard"]
            .with_context(
                active_model="stock.quant",
                active_ids=(quant_1 | quant_2).ids,
            )
            .create(
                {
                    "picking_type_id": self.lock_picking_type.id,
                }
            )
        )
        wizard.action_lock()

        self.assertTrue(quant_1.is_locked_by_picking)
        self.assertTrue(quant_2.is_locked_by_picking)
        self.assertEqual(quant_1.lock_move_count, 1)
        self.assertEqual(quant_2.lock_move_count, 1)
        lock_move_1 = self.env["stock.move"].search(
            [("quant_lock_quant_id", "=", quant_1.id)], limit=1
        )
        lock_move_2 = self.env["stock.move"].search(
            [("quant_lock_quant_id", "=", quant_2.id)], limit=1
        )
        self.assertEqual(lock_move_1.state, "assigned")
        self.assertEqual(lock_move_2.state, "assigned")
        (quant_1 | quant_2).action_unlock_quant()

        self.assertFalse(quant_1.is_locked_by_picking)
        self.assertFalse(quant_2.is_locked_by_picking)
        self.assertEqual(lock_move_1.state, "cancel")
        self.assertEqual(lock_move_2.state, "cancel")

    def test_lock_moves_not_merged_for_distinct_quants(self):
        lot2 = self.env["stock.lot"].create(
            {
                "name": "LOCK-LOT-002",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 2.0, lot_id=self.lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 2.0, lot_id=lot2
        )

        quant_1 = self._get_exact_quant(
            self.product,
            self.stock_location,
            lot=self.lot,
        )
        quant_2 = self._get_exact_quant(
            self.product,
            self.stock_location,
            lot=lot2,
        )
        self.assertEqual(len(quant_1), 1)
        self.assertEqual(len(quant_2), 1)

        move_1 = self.env["stock.move"].create(
            {
                "name": "Lock move 1",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": self.lock_picking_type.id,
                "quant_lock_quant_id": quant_1.id,
                "company_id": self.env.company.id,
            }
        )
        move_2 = self.env["stock.move"].create(
            {
                "name": "Lock move 2",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.output_location.id,
                "picking_type_id": self.lock_picking_type.id,
                "quant_lock_quant_id": quant_2.id,
                "company_id": self.env.company.id,
            }
        )

        confirmed_moves = (move_1 | move_2)._action_confirm()
        self.assertEqual(len(confirmed_moves), 2)
        self.assertNotEqual(
            confirmed_moves[0].quant_lock_quant_id.id,
            confirmed_moves[1].quant_lock_quant_id.id,
        )
