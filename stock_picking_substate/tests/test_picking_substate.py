# Copyright 2022 ArcheTI (https://archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)..
from odoo.exceptions import ValidationError

from odoo.addons.stock.tests.common import TestStockCommon


class TestPickingSubstate(TestStockCommon):
    def setUp(self):
        super(TestPickingSubstate, self).setUp()

        self.substate_preparation = self.env.ref(
            "stock_picking_substate.base_substate_preparation"
        )
        self.substate_wait_docs = self.env.ref(
            "stock_picking_substate.base_substate_wait_docs"
        )
        self.substate_valid_docs = self.env.ref(
            "stock_picking_substate.base_substate_valid_docs"
        )

    def test_picking_order_substate(self):
        picking_test1 = self.env["stock.picking"].create(
            {
                "location_id": self.pack_location,
                "location_dest_id": self.customer_location,
                "picking_type_id": self.picking_type_out,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.productA.name,
                            "product_id": self.productA.id,
                            "product_uom": self.productA.uom_id.id,
                            "product_uom_qty": 5,
                            "location_id": self.pack_location,
                            "location_dest_id": self.customer_location,
                        },
                    )
                ],
            }
        )
        self.assertTrue(picking_test1.state == "draft")
        self.assertTrue(picking_test1.substate_id == self.substate_preparation)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            picking_test1.substate_id = self.substate_valid_docs
        # Test that validation of the picking change substate_id
        picking_test1.action_confirm()
        self.assertTrue(picking_test1.state == "confirmed")
        self.assertTrue(picking_test1.substate_id == self.substate_wait_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        picking_test1.action_cancel()
        self.assertTrue(picking_test1.state == "cancel")
        self.assertTrue(not picking_test1.substate_id)
