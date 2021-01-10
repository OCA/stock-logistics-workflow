# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.stock.tests.common2 import TestStockCommon


class TestQtyDone(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_3")

    def test_qty_done(self):
        self.warehouse_1.in_type_id.qty_done_constraint = True
        move = self._create_move_in(
            self.product, self.warehouse_1, create_picking=True, product_uom_qty=3.0
        )
        move.picking_id.action_assign()
        self.assertEquals(3.0, move.picking_id.move_line_ids.product_qty)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            move.picking_id.move_line_ids.qty_done = 4
        move.picking_id.move_line_ids.qty_done = 2
