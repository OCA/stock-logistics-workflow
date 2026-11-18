# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockReturnPickingDescription(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True}
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "picking_type_id": cls.picking_type_in.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "description_picking": "Original description",
                        }
                    )
                ],
            }
        )

    def test_description_shown_from_move(self):
        """Description from the original move should appear in the wizard and carry
        over to the resulting return move upon confirmation."""
        self.picking.move_ids._action_confirm()
        self.picking.move_ids.picked = True
        self.picking.move_ids._action_done()
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=self.picking.id, active_model="stock.picking")
            .create({})
        )
        self.assertEqual(
            wizard.product_return_moves.description, "Original description"
        )
        wizard.product_return_moves.description = "Updated description"
        wizard.product_return_moves.quantity = 5.0
        res = wizard.action_create_returns()
        return_picking = self.env["stock.picking"].browse(res["res_id"])
        self.assertEqual(
            return_picking.move_ids.description_picking, "Updated description"
        )
