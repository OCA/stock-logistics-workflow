# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


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
        self.picking.move_line_ids.quantity = 1.0
        res = self.picking.button_validate()
        return res

    def test_backorder_strategy_cancel(self):
        """Set strategy for stock.picking_type_in to cancel
        Receive picking
        Check the backorder state is cancel
        """
        self.picking_type.create_backorder = "cancel"
        self._process_picking()
        backorder = self.picking_obj.search([("backorder_id", "=", self.picking.id)])
        self.assertTrue(backorder)
        self.assertEqual("cancel", backorder.state)
