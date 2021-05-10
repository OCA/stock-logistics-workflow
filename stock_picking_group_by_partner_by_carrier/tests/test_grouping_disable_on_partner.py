# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestGroupByBase


class TestGroupByDisabledOnPartner(TestGroupByBase):
    """Check we fallback on Odoo standard behavior if we disable the grouping
    feature on the partner.

    Tests are almost the same than the ones in 'test_grouping' module
    test assertions being different.
    """

    def setUp(self):
        super().setUp()
        self.partner.disable_picking_grouping = True

    def test_sale_stock_merge_same_partner_no_carrier(self):
        """2 sale orders for the same partner, without carrier

        -> the pickings are not merged
        """
        so1 = self._get_new_sale_order()
        so2 = self._get_new_sale_order(amount=11)
        so1.action_confirm()
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)

    def test_sale_stock_merge_same_carrier(self):
        """2 sale orders for the same partner, with same carrier

        -> the pickings are not merged
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for the sales, and it is shared
        self.assertTrue(so1.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking are their respective sale orders
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so2.picking_ids[0].origin)
        self.assertTrue(so2.name not in so1.picking_ids[0].origin)
        self.assertTrue(so1.name not in so2.picking_ids[0].origin)

    def test_backorder_picking_merge(self):
        """1st sale order ship is printed, 2nd sale order not merged.
        Partial delivery of so1

        -> backorder is not merged with so2 picking

        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so1.picking_ids.do_print_picking()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        pick = so1.picking_ids
        move = pick.move_lines[0]
        move.quantity_done = 5
        pick.with_context(cancel_backorder=False).action_done()
        self.assertFalse(so2.picking_ids & so1.picking_ids)
        self.assertEqual(so2.picking_ids.sale_ids, so2)
        self.assertEqual(so1.picking_ids.sale_ids, so1)

    def test_cancelling_sale_order1(self):
        """1st sale order is cancelled

        -> picking is also canceled
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        so1.action_cancel()
        self.assertEqual(so1.picking_ids.state, "cancel")
        self.assertNotEqual(so2.picking_ids.state, "cancel")
        so1_moves = so1.picking_ids.move_lines
        so2_moves = so2.picking_ids.move_lines
        self.assertEqual(so1_moves.mapped("state"), ["cancel"])
        self.assertEqual(so2_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so1.state, "cancel")
        self.assertEqual(so2.state, "sale")

    def test_cancelling_sale_order2(self):
        """2nd sale order is cancelled

        -> picking is also canceled
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        so2.action_cancel()
        self.assertNotEqual(so1.picking_ids.state, "cancel")
        self.assertEqual(so2.picking_ids.state, "cancel")
        so1_moves = so1.picking_ids.move_lines
        so2_moves = so2.picking_ids.move_lines
        self.assertEqual(so1_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so2_moves.mapped("state"), ["cancel"])
        self.assertEqual(so1.state, "sale")
        self.assertEqual(so2.state, "cancel")

    def test_delivery_multi_step(self):
        """the warehouse uses pick + ship

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick_pack(self):
        """the warehouse uses pick + pack + ship (with grouping enabled on pack)

        -> none of the transfers are grouped (pick, pack or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_pack_ship"
        warehouse.pick_type_id.group_pickings = False
        warehouse.pack_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 3)
        self.assertEqual(len(so2.picking_ids), 3)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_cancel_so1(self):
        """the warehouse uses pick + ship. Cancel SO1

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so1.action_cancel()
        self.assertEqual(so1.state, "cancel")
        self.assertEqual(so1.picking_ids.mapped("state"), ["cancel", "cancel"])
        self.assertNotEqual(so2.state, "cancel")

    def test_delivery_multi_step_cancel_so2(self):
        """the warehouse uses pick + ship. Cancel SO2

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so2.action_cancel()
        self.assertEqual(so2.state, "cancel")
        self.assertEqual(so2.picking_ids.mapped("state"), ["cancel", "cancel"])
        self.assertNotEqual(so1.state, "cancel")

    def test_delivery_multi_step_group_pick_cancel_so1(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so1.action_cancel()
        # ship & pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick_cancel_so2(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so2.action_cancel()
        # ship & pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_cancel_so1_create_so3(self):
        """the warehouse uses pick + ship. Cancel SO1, create SO3

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so1.action_cancel()
        so3 = self._get_new_sale_order(amount=12, carrier=self.carrier1)
        so3.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids & so3.picking_ids)

    def test_sale_stock_merge_procurement_group(self):
        """sale orders are not merged, procurement groups are not merged

        Ensure that the procurement group is linked only to its SO
        Ensure that printed transfers keep their procurement group.
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.name = "SO1"
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.name = "SO2"
        so1.action_confirm()
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        # the group is the same on the move lines and picking
        picking1 = so1.picking_ids
        picking2 = so2.picking_ids
        self.assertEqual(picking1.group_id, picking1.move_lines.group_id)
        group1 = picking1.group_id
        group2 = picking2.group_id
        # each group is related only to the relevant sale order
        self.assertEqual(group1.sale_ids, so1)
        self.assertEqual(group1.name, so1.name)
        self.assertEqual(group2.sale_ids, so2)
        self.assertEqual(group2.name, so2.name)

    def test_create_backorder(self):
        """Ensure there is no regression when group pickings is disabled on
        partner when we confirm a partial qty on a picking to create a backorder.
        """
        so = self._get_new_sale_order(amount=10, carrier=self.carrier1)
        so.name = "SO TEST"
        so.action_confirm()
        picking = so.picking_ids
        # picking.picking_type_id.group_pickings = False
        self._update_qty_in_location(
            picking.location_id,
            so.order_line[0].product_id,
            so.order_line[0].product_uom_qty,
        )
        picking.action_assign()
        line = picking.move_lines[0].move_line_ids
        line.qty_done = line.product_uom_qty / 2
        picking.action_done()
        self.assertEqual(picking.state, "done")
        self.assertTrue(picking.backorder_ids)
        self.assertNotEqual(picking, picking.backorder_ids)
