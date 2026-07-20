# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestRestrictCancelStockMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"reception_steps": "three_steps"})
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.input_loc = cls.warehouse.wh_input_stock_loc_id
        cls.qc_loc = cls.warehouse.wh_qc_stock_loc_id

        cls.internal_pt = cls.warehouse.int_type_id
        cls.internal_pt.active = True
        cls.internal_pt.restrict_cancel_with_orig_move = True

        cls.dummy_product = (
            cls.env["product.template"]
            .create(
                {
                    "name": "Dummy product",
                    "type": "consu",
                    "purchase_ok": True,
                    "is_storable": True,
                }
            )
            .product_variant_ids
        )

        cls.input_to_qc_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.internal_pt.id,
                "location_id": cls.input_loc.id,
                "location_dest_id": cls.qc_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.dummy_product.name,
                            "product_id": cls.dummy_product.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "location_id": cls.input_loc.id,
                        },
                    )
                ],
            }
        )
        cls.input_to_qc_picking.action_confirm()
        cls.qc_to_stock_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.internal_pt.id,
                "location_id": cls.qc_loc.id,
                "location_dest_id": cls.stock_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.dummy_product.name,
                            "product_id": cls.dummy_product.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "location_id": cls.qc_loc.id,
                        },
                    )
                ],
            }
        )
        cls.qc_to_stock_picking.action_confirm()
        # Link moves
        cls.qc_to_stock_picking.move_ids.move_orig_ids |= (
            cls.input_to_qc_picking.move_ids
        )

    def test_restrict(self):
        qc_to_stock_move = self.qc_to_stock_picking.move_ids
        self.assertNotEqual(qc_to_stock_move.state, "cancel")
        self.assertNotEqual(self.input_to_qc_picking.move_ids.state, "cancel")
        with self.assertRaises(UserError):
            self.qc_to_stock_picking.action_cancel()
        self.input_to_qc_picking.action_cancel()
        self.assertEqual(qc_to_stock_move.state, "cancel")
        self.assertEqual(self.input_to_qc_picking.move_ids.state, "cancel")

    def test_no_restriction_when_flag_disabled(self):
        self.internal_pt.restrict_cancel_with_orig_move = False
        upstream = self.env["stock.picking"].create(
            {
                "picking_type_id": self.internal_pt.id,
                "location_id": self.input_loc.id,
                "location_dest_id": self.qc_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.dummy_product.name,
                            "product_id": self.dummy_product.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "location_id": self.input_loc.id,
                        },
                    )
                ],
            }
        )
        upstream.action_confirm()
        downstream = self.env["stock.picking"].create(
            {
                "picking_type_id": self.internal_pt.id,
                "location_id": self.qc_loc.id,
                "location_dest_id": self.stock_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.dummy_product.name,
                            "product_id": self.dummy_product.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "location_id": self.qc_loc.id,
                        },
                    )
                ],
            }
        )
        downstream.action_confirm()
        downstream.move_ids.move_orig_ids |= upstream.move_ids
        # Cancelling the downstream picking must succeed even though the
        # upstream move is still in progress, because the flag is off.
        downstream.action_cancel()
        self.assertEqual(downstream.move_ids.state, "cancel")

    def test_do_not_restrict(self):
        # When this picking is created, odoo will apply push rules on each
        # stock move to generate putaway moves. These putaway moves are created
        # first by copying each input moves, before being merged together, thus
        # trigger a move cancellation which should be allowed anyway.
        pick = self.env["stock.picking"].create(
            {
                "picking_type_id": self.internal_pt.id,
                "location_id": self.input_loc.id,
                "location_dest_id": self.qc_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.dummy_product.name,
                            "product_id": self.dummy_product.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "location_id": self.input_loc.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.dummy_product.name,
                            "product_id": self.dummy_product.id,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 3,
                            "location_id": self.input_loc.id,
                        },
                    ),
                ],
            }
        )
        pick.action_confirm()
        qc_to_stock_move = pick.move_ids
        # qc_to_stock_move has merged all the moves so its quantity is 4
        self.assertEqual(qc_to_stock_move.product_uom_qty, 4)
