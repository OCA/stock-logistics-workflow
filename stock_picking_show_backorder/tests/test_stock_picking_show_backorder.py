# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestStockPickingShowBackorder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": cls.picking.id,
                "product_id": cls.product.id,
                "product_uom_qty": 20,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )

    def test_stock_picking_show_backorder(self):
        # Picking in draf state
        self.assertEqual(self.picking.state, "draft")
        # Confirm picking
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "assigned")
        move_line = self.env["stock.move.line"].search(
            [("picking_id", "=", self.picking.id)], limit=1
        )
        move_line.qty_done = 1.0
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
        # The backorder should be created
        self.assertEqual(len(self.picking.backorder_ids), 1, "It should be 1")
