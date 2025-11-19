# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged

from .common import TestProcurementGroupCarrierCommon


@tagged("post_install", "-at_install")
class TestProcurementGroupCarrier(TestProcurementGroupCarrierCommon):
    @classmethod
    def create_return(cls, move, qty_to_return):
        picking = move.picking_id
        return_picking_type = picking.picking_type_id.return_picking_type_id
        wiz_values = {
            "picking_id": picking.id,
            "location_id": return_picking_type.default_location_dest_id.id,
            "product_return_moves": [
                (
                    0,
                    0,
                    {
                        "move_id": move.id,
                        "product_id": move.product_id.id,
                        "quantity": qty_to_return,
                        "uom_id": move.product_uom.id,
                    },
                )
            ],
        }
        return_wiz = (
            cls.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_ids=[picking.id],
                active_model="stock.picking",
            )
            .create(wiz_values)
        )
        action = return_wiz.create_returns()
        cancel_picking = move.picking_id.browse(action["res_id"])
        return cancel_picking

    def test_return_new_group(self):
        order = self._create_sale_order([(self.product, 10.0)], carrier=self.carrier)
        order.action_confirm()
        out_picking = order.picking_ids
        out_group = out_picking.group_id
        out_carrier = out_picking.carrier_id

        move = order.picking_ids.move_ids
        cancel_picking = self.create_return(move, 5)
        self.assertTrue(cancel_picking.group_id)
        self.assertNotEqual(cancel_picking.group_id, out_group)
        self.assertFalse(cancel_picking.group_id.carrier_id)
        self.assertFalse(cancel_picking.carrier_id)
        self.assertEqual(out_picking.carrier_id, out_carrier)
