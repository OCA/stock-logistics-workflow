# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from unittest.mock import patch

from odoo.addons.stock_account.tests.common import TestStockValuationCommon


class TestFifoHook(TestStockValuationCommon):
    _test_user_groups = None

    def _patch_hook(self):
        calls = []

        def _record(self, candidate_move, qty_taken, value_taken, valued_move):
            calls.append((candidate_move, qty_taken, value_taken, valued_move))
            return True

        return calls, patch.object(
            type(self.env["product.product"]),
            "_run_fifo_prepare_candidate_update",
            _record,
        )

    def _patch_reset(self):
        resets = []

        def _reset(self, valued_moves):
            resets.append(valued_moves)
            return True

        return resets, patch.object(
            type(self.env["product.product"]), "_run_fifo_correction_reset", _reset
        )

    def test_prepare_candidate_update_called(self):
        product = self.product_fifo
        move_in_1 = self._make_in_move(product, 10, 10)
        move_in_2 = self._make_in_move(product, 10, 8)
        calls, hook = self._patch_hook()
        with hook:
            move_out = self._make_out_move(product, 15)
            self.assertEqual(move_out.value, -140.0)
            self.assertEqual(
                calls,
                [(move_in_1, 10.0, 100.0, move_out), (move_in_2, 5.0, 40.0, move_out)],
            )
            calls.clear()
            self.assertEqual(product._get_fifo_value(5), 40.0)
        self.assertEqual(calls, [(move_in_2, 5.0, 40.0, None)])

    def test_prepare_candidate_update_batch(self):
        product = self.product_fifo
        move_in_1 = self._make_in_move(product, 10, 10)
        move_in_2 = self._make_in_move(product, 10, 8)
        moves_out = self.env["stock.move"].create(
            [
                {
                    "product_id": product.id,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "picking_type_id": self.picking_type_out.id,
                    "product_uom_qty": qty,
                }
                for qty in (10, 5)
            ]
        )
        moves_out._action_confirm(merge=False)
        moves_out._action_assign()
        move_out_1, move_out_2 = moves_out
        move_out_1.quantity = 10
        move_out_2.quantity = 5
        moves_out.picked = True
        calls, hook = self._patch_hook()
        with hook:
            moves_out._action_done()
        self.assertEqual(move_out_1.value, -100.0)
        self.assertEqual(move_out_2.value, -40.0)
        self.assertEqual(
            calls,
            [
                (move_in_1, 10.0, 100.0, move_out_1),
                (move_in_2, 5.0, 40.0, move_out_2),
            ],
        )

    def test_prepare_candidate_update_lot(self):
        product = self.product_fifo.create(
            {
                **self.product_common_vals,
                "name": "Lot Valuated FIFO",
                "categ_id": self.category_fifo.id,
                "lot_valuated": True,
                "tracking": "lot",
            }
        )
        lot_1, lot_2 = self.env["stock.lot"].create(
            [{"name": name, "product_id": product.id} for name in ("L1", "L2")]
        )
        move_in_1 = self._make_in_move(product, 10, 10, lot_ids=[lot_1])
        move_in_2 = self._make_in_move(product, 10, 6, lot_ids=[lot_2])
        calls, hook = self._patch_hook()
        with hook:
            move_out = self._make_out_move(product, 4, lot_ids=[lot_1, lot_2])
        self.assertEqual(move_out.value, -32.0)
        self.assertEqual(
            calls,
            [(move_in_1, 2.0, 20.0, move_out), (move_in_2, 2.0, 12.0, move_out)],
        )

    def test_prepare_candidate_update_correction(self):
        product = self.product_fifo
        move_in_1 = self._make_in_move(product, 5, 10)
        move_out = self._make_out_move(product, 8)
        self.assertEqual(move_out.value, -80.0)
        calls, hook = self._patch_hook()
        resets, reset = self._patch_reset()
        with hook, reset:
            move_in_2 = self._make_in_move(product, 10, 6)
        self.assertEqual(move_out.value, -68.0)
        self.assertEqual(resets, [move_out])
        self.assertEqual(
            calls,
            [(move_in_1, 5.0, 50.0, move_out), (move_in_2, 3.0, 18.0, move_out)],
        )
