# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestMoveBackorder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.picking_t_out = cls.env.ref("stock.picking_type_out")
        cls.picking_obj = cls.env["stock.picking"]
        cls.product = cls.env.ref("product.product_product_6")
        cls.unit = cls.env.ref("uom.product_uom_unit")

        vals = {
            "picking_type_id": cls.picking_t_out.id,
            "origin": "OUT 1",
            "partner_id": cls.env.ref("base.res_partner_1").id,
            "location_id": cls.stock.id,
            "location_dest_id": cls.customers.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": "PRODUCT 6",
                        "product_uom_qty": 80.0,
                        "product_id": cls.product.id,
                        "product_uom": cls.unit.id,
                        "location_id": cls.stock.id,
                        "location_dest_id": cls.customers.id,
                        "move_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.env.ref(
                                        "product.product_product_6"
                                    ).id,
                                    "qty_done": 10.0,
                                    "product_uom_id": cls.env.ref(
                                        "uom.product_uom_unit"
                                    ).id,
                                    "location_id": cls.stock.id,
                                    "location_dest_id": cls.customers.id,
                                },
                            )
                        ],
                    },
                )
            ],
        }
        cls.picking = cls.picking_obj.create(vals)
        cls.move = cls.picking.move_lines

    def test_backorder(self):
        """
        Do a partial move with backorder
        Check if there is one
        Check if the move has childs
        Check if the backorder move has ancestor
        """
        self.move._action_done()
        self.assertEquals(
            "done", self.move.state,
        )
        self.assertTrue(self.move.child_ids)
        self.assertEquals(
            self.move.child_ids.picking_id.backorder_id, self.move.picking_id
        )
        child = self.move.child_ids
        self.assertEquals(self.move, child.ancestor_ids)
