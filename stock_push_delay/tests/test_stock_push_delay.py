from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestPacking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPacking, cls).setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("lot_stock_id", "=", cls.stock_location.id)], limit=1
        )
        cls.warehouse.reception_steps = "two_steps"

        cls.productA = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )

    def test_push_delay(self):
        """Checks that the push picking is delayed"""
        receipt_form = Form(self.env["stock.picking"])
        receipt_form.picking_type_id = self.warehouse.in_type_id
        with receipt_form.move_ids_without_package.new() as move_line:
            move_line.product_id = self.productA
            move_line.product_uom_qty = 1
        receipt = receipt_form.save()
        receipt.action_confirm()
        # Checks an internal transfer was not created.
        internal_transfer = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.warehouse.int_type_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertNotEqual(internal_transfer.origin, receipt.name)
        receipt._action_done()
        # Checks an internal transfer was created.
        internal_transfer = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.warehouse.int_type_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertEqual(internal_transfer.origin, receipt.name)
