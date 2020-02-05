# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingScrapQuick(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner - test", "customer": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "product"}
        )
        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "quantity": 50.0,
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test",
                "product_id": cls.product.id,
                "picking_id": cls.picking.id,
                "picking_type_id": cls.picking_type_out.id,
                "product_uom_qty": 2.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "location_dest_id": cls.customer_location.id,
                "procure_method": "make_to_stock",
            }
        )

    def test_scrap_load_view(self):
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 2.0
        self.picking.button_validate()
        wiz = (
            self.env["wiz.stock.picking.scrap"]
            .with_context(active_id=self.picking.id)
            .create({})
        )
        self.assertEqual(len(wiz.line_ids), 1)

    def test_scrap_picking_not_done(self):
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 2.0
        with self.assertRaises(UserError):
            self.env["wiz.stock.picking.scrap"].with_context(
                active_id=self.picking.id
            ).create({})

    def test_scrap_more_qty_that_done(self):
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 2.0
        self.picking.button_validate()
        wiz = (
            self.env["wiz.stock.picking.scrap"]
            .with_context(active_id=self.picking.id)
            .create({})
        )
        wiz.line_ids.quantity = 10.0
        with self.assertRaises(UserError):
            wiz.create_scrap()

    def test_do_scrap(self):
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 2.0
        self.picking.button_validate()
        wiz = (
            self.env["wiz.stock.picking.scrap"]
            .with_context(active_id=self.picking.id)
            .create({})
        )
        scraps = wiz.create_scrap()
        self.assertEqual(len(scraps), 1)
