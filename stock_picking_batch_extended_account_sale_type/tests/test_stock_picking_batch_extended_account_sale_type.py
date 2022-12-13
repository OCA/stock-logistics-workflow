# Copyright 2019 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.stock_picking_batch_extended_account.tests import (
    test_stock_picking_batch_extended_account as test_bp_account,
)


class TestStockPickingBatchExtendedAccountSaleType(
    test_bp_account.TestStockPickingBatchExtendedAccount
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_type = cls.env["sale.order.type"].create(
            {"name": "sale type for tests", "batch_picking_auto_invoice": True}
        )
        cls.partner.write(
            {"sale_type": cls.sale_type.id, "batch_picking_auto_invoice": "no"}
        )
        cls.partner2.write(
            {"sale_type": cls.sale_type.id, "batch_picking_auto_invoice": "sale_type"}
        )

    def test_create_invoice_from_bp_sale_type(self):
        self.order1 = self._create_sale_order(self.partner)
        self.order2 = self._create_sale_order(self.partner2)
        self.order1.action_confirm()
        self.order2.action_confirm()
        pickings = self.order1.picking_ids + self.order2.picking_ids
        move_lines = pickings.mapped("move_line_ids")
        move_lines.qty_done = 1.0
        bp = self._create_batch_picking(pickings)
        bp.action_assign()
        bp.action_done()
        self.assertFalse(self.order1.invoice_ids)
        self.assertTrue(self.order2.invoice_ids)
