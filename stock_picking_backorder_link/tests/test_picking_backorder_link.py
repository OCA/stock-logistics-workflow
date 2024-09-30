# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestPickingBackorderLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create the picking."""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.company.stock_picking_backorder_link = True

        cls.picking_obj = cls.env["stock.picking"]
        move_obj = cls.env["stock.move"]

        cls.picking_type = cls.env.ref("stock.picking_type_in")

        product = cls.env.ref("product.product_product_13")
        loc_supplier_id = cls.env.ref("stock.stock_location_suppliers").id
        loc_stock_id = cls.env.ref("stock.stock_location_stock").id

        cls.picking1 = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
            }
        )
        cls.move1 = move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking1.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 2,
            }
        )
        cls.picking2 = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "backorder_id": cls.picking1.id,
            }
        )
        cls.move2 = move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking2.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 2,
            }
        )
        cls.picking3 = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
            }
        )
        cls.move3 = move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking3.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 4,
                "move_orig_ids": [(4, m.id) for m in [cls.move1, cls.move2]],
            }
        )
        cls.picking4 = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
            }
        )
        cls.move4 = move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking4.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 1,
                "move_orig_ids": [(4, m.id) for m in [cls.move3]],
            }
        )
        cls.picking5 = cls.picking_obj.create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
            }
        )
        cls.move5 = move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking5.id,
                "product_uom": product.uom_id.id,
                "location_id": loc_stock_id,
                "location_dest_id": loc_stock_id,
                "product_id": product.id,
                "product_uom_qty": 3,
                "move_orig_ids": [(4, m.id) for m in [cls.move3]],
            }
        )
        cls.picking1.action_confirm()
        cls.picking2.action_confirm()
        cls.picking3.action_confirm()
        cls.picking4.action_confirm()
        cls.picking5.action_confirm()

    def test_validate_less_qty(self):
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move3.product_uom_qty, 4)
        self.assertEqual(self.move3.state, "waiting")
        self.assertEqual(self.move4.product_uom_qty, 1)
        self.assertEqual(self.move4.state, "waiting")
        self.assertEqual(self.move5.product_uom_qty, 3)
        self.assertEqual(self.move5.state, "waiting")
        self.picking1.move_line_ids.qty_done = 2.0
        self.picking1.button_validate()
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move3.product_uom_qty, 4)
        self.assertEqual(self.move3.state, "partially_available")
        self.assertEqual(self.move4.product_uom_qty, 1)
        self.assertEqual(self.move4.state, "waiting")
        self.assertEqual(self.move5.product_uom_qty, 3)
        self.assertEqual(self.move5.state, "waiting")
        self.picking3.move_line_ids.qty_done = 2.0
        self.picking3.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=[self.picking3.id]
        ).button_validate()
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "cancel")
        self.assertEqual(self.move4.product_uom_qty, 1)
        self.assertEqual(self.move4.state, "cancel")
        self.assertEqual(self.move5.product_uom_qty, 2)
        self.assertEqual(self.move5.state, "assigned")

    def test_cancel_backorder(self):
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move3.product_uom_qty, 4)
        self.assertEqual(self.move3.state, "waiting")
        self.picking1.move_line_ids.qty_done = 2.0
        self.picking1.button_validate()
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "assigned")
        self.assertEqual(self.move3.product_uom_qty, 4)
        self.assertEqual(self.move3.state, "partially_available")
        self.picking3.move_line_ids.qty_done = 2.0
        res_dict = self.picking3.button_validate()
        backorder_wizard = Form(
            self.env["stock.backorder.confirmation"].with_context(**res_dict["context"])
        ).save()
        backorder_wizard.process()
        backorder = self.picking_obj.search([("backorder_id", "=", self.picking3.id)])
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "assigned")
        backorder.action_cancel()
        self.assertEqual(self.move2.product_uom_qty, 2)
        self.assertEqual(self.move2.state, "cancel")
