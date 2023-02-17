# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestBackorderStrategy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create the picking."""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.picking_obj = cls.env["stock.picking"]
        move_obj = cls.env["stock.move"]

        cls.picking_type = cls.env.ref("stock.picking_type_in")

        product = cls.env.ref("product.product_product_13")
        loc_supplier_id = cls.env.ref("stock.stock_location_suppliers").id
        loc_stock_id = cls.env.ref("stock.stock_location_stock").id

        cls.picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
            }
        )
        move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 2,
            }
        )
        cls.picking.action_confirm()

    def _process_picking(self):
        """Receive partially the picking"""
        self.picking.move_line_ids.qty_done = 1.0
        res = self.picking.button_validate()
        return res

    def test_backorder_strategy_create(self):
        """Check strategy for stock.picking_type_in is create
        Receive picking
        Check backorder is created
        """
        self.picking_type.backorder_strategy = "create"
        self._process_picking()
        backorder = self.picking_obj.search([("backorder_id", "=", self.picking.id)])
        self.assertTrue(backorder)

    def test_backorder_strategy_no_create(self):
        """Set strategy for stock.picking_type_in to no_create
        Receive picking
        Check there is no backorder
        Check if there is one move done and one move cancelled
        """
        self.picking_type.backorder_strategy = "no_create"
        self._process_picking()
        backorder = self.picking_obj.search([("backorder_id", "=", self.picking.id)])
        self.assertFalse(backorder)
        states = list(set(self.picking.move_lines.mapped("state")))
        self.assertEqual(
            "done",
            self.picking.state,
        )
        self.assertListEqual(
            ["cancel", "done"],
            sorted(states),
        )

    def test_backorder_strategy_cancel(self):
        """Set strategy for stock.picking_type_in to cancel
        Receive picking
        Check the backorder state is cancel
        """
        self.picking_type.backorder_strategy = "cancel"
        self._process_picking()
        backorder = self.picking_obj.search([("backorder_id", "=", self.picking.id)])
        self.assertTrue(backorder)
        self.assertEqual("cancel", backorder.state)

    def test_backorder_strategy_manual(self):
        """Set strategy for stock.picking_type_in to manual
        Receive picking
        Check the backorder wizard is launched
        """
        self.assertEqual("manual", self.picking_type.backorder_strategy)
        res_dict = self._process_picking()
        backorder_wizard = Form(
            self.env["stock.backorder.confirmation"].with_context(**res_dict["context"])
        ).save()
        backorder_wizard.process()
        self.assertEqual(
            "done",
            self.picking.state,
        )
        backorder_exist = self.picking_obj.search(
            [("backorder_id", "=", self.picking.id)]
        )
        self.assertEqual(len(backorder_exist), 1, "Back order should be created.")
