# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestStockMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()
        cls.picking_obj = cls.env["stock.picking"]
        move_obj = cls.env["stock.move"]

        cls.picking_type = cls.env.ref("stock.picking_type_in")

        product_1 = cls.env.ref("product.product_product_13")
        product_2 = cls.env.ref("product.product_product_9")
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
                "product_uom": product_1.uom_id.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "product_id": product_1.id,
                "product_uom_qty": 2,
            }
        )

        move_obj.create(
            {
                "name": "/",
                "picking_id": cls.picking.id,
                "product_uom": product_2.uom_id.id,
                "location_id": loc_supplier_id,
                "location_dest_id": loc_stock_id,
                "product_id": product_2.id,
                "product_uom_qty": 4,
            }
        )
        cls.picking.action_confirm()

    def test_00(self):
        """
        Data:
            A picking with 2 stock moves linked to 2 pack operations
        Test case:
            Cancel 1 move
        Expected result:
            1 pack operation is deleted
        """
        self.assertEquals(len(self.picking.pack_operation_ids), 2)
        self.assertEquals(len(self.picking.move_lines), 2)
        self.picking.move_lines[0].action_cancel()
        self.assertEquals(len(self.picking.pack_operation_ids), 1)

    def test_02(self):
        """
        Data:
            A picking with 2 stock moves linked to 2 pack operations
        Test case:
            Cancel the picking
        Expected result:
            All the pack operations are deleted
        """
        self.assertEquals(len(self.picking.pack_operation_ids), 2)
        self.assertEquals(len(self.picking.move_lines), 2)
        self.picking.action_cancel()
        self.assertEquals(len(self.picking.pack_operation_ids), 0)
