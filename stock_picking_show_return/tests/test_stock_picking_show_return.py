# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingShowReturn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        picking_type = cls.env.ref("stock.picking_type_internal")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": (
                                picking_type.default_location_dest_id.id
                            ),
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 1,
                        }
                    ),
                ],
            }
        )

    def get_return_picking_wizard(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return stock_return_picking_form.save()

    def test_returned_ids_field(self):
        self.picking.action_assign()
        self.picking.move_line_ids.quantity = 1
        self.picking.move_line_ids.picked = True
        self.picking._action_done()
        wizard = self.get_return_picking_wizard(self.picking)
        wizard.create_returns()
        self.picking._compute_returned_ids()
        self.assertTrue(self.picking.returned_ids)

    def test_source_picking_id_field(self):
        self.picking.action_assign()
        self.picking.move_line_ids.quantity = 1
        self.picking.move_line_ids.picked = True
        self.picking._action_done()
        wizard = self.get_return_picking_wizard(self.picking)
        wizard.create_returns()
        self.picking._compute_returned_ids()
        picking_returned = self.picking.returned_ids[0]
        # Get first picking returned to check if origin is self.picking
        picking_origin = picking_returned.source_picking_id
        self.assertEqual(picking_origin, self.picking)
        # Open origin returned picking form view
        action = picking_returned.action_show_source_picking()
        self.assertEqual(action["res_id"], self.picking.id)
