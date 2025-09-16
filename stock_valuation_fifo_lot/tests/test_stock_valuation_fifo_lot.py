# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_valuation_fifo_lot.tests.common import (
    TestStockValuationFifoCommon,
)


class TestStockValuationFifoLot(TestStockValuationFifoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_out_picking_return(self):
        in_pick, in_moves = self.create_picking("in", self.lot1, ml_qty=5, price=10)
        self.create_landed_cost(in_pick, 10)
        out_pick, out_moves = self.create_picking("out", self.lot1, 1)
        self.return_picking(out_pick, 1)
        svls = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(60, sum(svls.mapped("value")))
