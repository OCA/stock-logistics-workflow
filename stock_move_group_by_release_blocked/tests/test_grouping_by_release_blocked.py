# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import tagged

from odoo.addons.stock_available_to_promise_release_block.tests.common import (
    BlockReleaseCommon,
)


@tagged("post_install", "-at_install")
class TestGroupByReleaseBlocked(BlockReleaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.group_pickings_by_release_blocked = True

    def _create_stock_move(self, location_id, location_dest_id):
        return self.env["stock.move"].create(
            {
                "name": "Test Move",
                "partner_id": self.partner_delta.id,
                "product_id": self.product1.id,
                "product_uom_qty": 5,
                "product_uom": self.product1.uom_id.id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )

    def test_group_by_release_blocked(self):
        move1 = self._create_stock_move(self.loc_stock, self.loc_customer)
        move1._action_confirm()

        # Blocked release move2 grouped into move1.picking_id
        move2 = self._create_stock_move(self.loc_stock, self.loc_customer)
        # The release will be blocked only on moves with ``need_release`` enabled
        move2.need_release = True
        move2.action_block_release()
        move2._action_confirm(merge=False)
        self.assertNotEqual(move1.picking_id, move2.picking_id)

        # Blocked release move3 grouped into move2.picking_id
        move3 = self._create_stock_move(self.loc_stock, self.loc_customer)
        move3.need_release = True
        move3.action_block_release()
        move3._action_confirm(merge=False)
        self.assertEqual(move2.picking_id, move3.picking_id)

        # Unblocked release move4 grouped into move1.picking_id
        move4 = self._create_stock_move(self.loc_stock, self.loc_customer)
        move4.action_block_release()
        move4._action_confirm(merge=False)
        self.assertEqual(move1.picking_id, move4.picking_id)
