# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestGroupByBase


class TestGroupBy(TestGroupByBase):
    def test_sale_stock_merge_same_partner_no_carrier(self):
        """2 sale orders for the same partner, without carrier

        -> the pickings are merged"""
        so1 = self._get_new_sale_order()
        so2 = self._get_new_sale_order(amount=11)
        so1.action_confirm()
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertEqual(so1.picking_ids, so2.picking_ids)

    def test_sale_stock_merge_same_carrier(self):
        """2 sale orders for the same partner, with same carrier

        -> the pickings are merged"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for the sales, and it is shared
        self.assertTrue(so1.picking_ids)
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking mentions both sales names
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so1.picking_ids[0].origin)

    def test_sale_stock_no_merge_different_carrier(self):
        """2 sale orders for the same partner, with different carriers

        -> the pickings are not merged"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier2)
        so1.action_confirm()
        so2.action_confirm()
        self.assertEqual(so1.picking_ids.carrier_id, self.carrier1)
        self.assertEqual(so2.picking_ids.carrier_id, self.carrier2)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so2.picking_ids[0].origin)

    def test_sale_stock_no_merge_carrier_set_only_on_one(self):
        """2 sale orders for the same partner, one with the other without

        -> the pickings are not merged"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=None)
        so1.action_confirm()
        so2.action_confirm()
        self.assertEqual(so1.picking_ids.carrier_id, self.carrier1)
        self.assertFalse(so2.picking_ids.carrier_id)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)

    def test_sale_stock_no_merge_same_carrier_picking_policy_one(self):
        """2 sale orders for the same partner, with same carrier, deliver at
        once picking policy

        -> the pickings are not merged

        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.picking_policy = "one"
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.picking_policy = "one"
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for each the sales, different
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking mentions both sales names
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so2.picking_ids[0].origin)

    def test_sale_stock_no_merge_same_carrier_mixed_picking_policy(self):
        """2 sale orders for the same partner, with same carrier, deliver at once
        picking policy for the 1st sale order.

        -> the pickings are not merged

        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.picking_policy = "one"
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for each the sales, different
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking mentions both sales names
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so2.picking_ids[0].origin)

    def test_printed_pick_no_merge(self):
        """1st sale order ship is printed, 2nd sale order not merged"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so1.picking_ids.do_print_picking()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)

    def test_backorder_picking_merge(self):
        """1st sale order ship is printed, 2nd sale order not merged.
        Partial delivery of so1

        -> backorder is merged with so2 picking

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
        self.assertTrue(so2.picking_ids & so1.picking_ids)
        self.assertEqual(so2.picking_ids.sale_ids, so1 + so2)

    def test_cancelling_sale_order1(self):
        """1st sale order is cancelled

        -> picking is still todo with only 1 stock move todo"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        so1.action_cancel()
        self.assertNotEqual(so1.picking_ids.state, "cancel")
        moves = so1.picking_ids.move_lines
        so1_moves = moves.filtered(lambda m: m.sale_line_id.order_id == so1)
        so2_moves = moves.filtered(lambda m: m.sale_line_id.order_id == so2)
        self.assertEqual(so1_moves.mapped("state"), ["cancel"])
        self.assertEqual(so2_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so1.state, "cancel")
        self.assertEqual(so2.state, "sale")

    def test_cancelling_sale_order1_before_create_order2(self):
        """1st sale order is cancelled

        -> picking is still todo with only 1 stock move todo"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so1.action_cancel()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_cancelling_sale_order2(self):
        """2nd sale order is cancelled

        -> picking is still todo with only 1 stock move todo"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        so2.action_cancel()
        self.assertNotEqual(so1.picking_ids.state, "cancel")
        moves = so1.picking_ids.move_lines
        so1_moves = moves.filtered(lambda m: m.sale_line_id.order_id == so1)
        so2_moves = moves.filtered(lambda m: m.sale_line_id.order_id == so2)
        self.assertEqual(so1_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so2_moves.mapped("state"), ["cancel"])
        self.assertEqual(so1.state, "sale")
        self.assertEqual(so2.state, "cancel")

    def test_delivery_multi_step(self):
        """the warehouse uses pick + ship

        -> shippings are grouped, pickings are not"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship should be shared between so1 and so2
        ships = so1.picking_ids & so2.picking_ids
        self.assertEqual(len(ships), 1)
        self.assertEqual(ships.picking_type_id, warehouse.out_type_id)
        # but not picks
        self.assertTrue(so1.picking_ids - so2.picking_ids)
        self.assertTrue(so2.picking_ids - so1.picking_ids)
        picks = (so1.picking_ids - so2.picking_ids) | (
            so2.picking_ids - so1.picking_ids
        )

        self.assertEqual(len(picks), 2)
        self.assertEqual(picks.mapped("picking_type_id"), warehouse.pick_type_id)

    def test_delivery_multi_step_group_pick(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> shippings are grouped, as well as pickings"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship & pick should be shared between so1 and so2
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        transfers = so1.picking_ids
        self.assertEqual(len(transfers), 2)
        ships = transfers.filtered(lambda o: o.picking_type_id == warehouse.out_type_id)
        picks = transfers.filtered(
            lambda o: o.picking_type_id == warehouse.pick_type_id
        )
        self.assertEqual(len(ships), 1)
        self.assertEqual(len(picks), 1)
        self.assertFalse(so1.picking_ids - so2.picking_ids)

    def test_delivery_multi_step_group_pick_pack(self):
        """the warehouse uses pick + pack + ship (with grouping enabled on pack)

        -> shippings are grouped, as well as pickings"""
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
        # ship & pack should be shared between so1 and so2, but not pick
        all_transfers = so1.picking_ids | so2.picking_ids
        common_transfers = so1.picking_ids & so2.picking_ids
        self.assertEqual(len(all_transfers), 4)
        self.assertEqual(len(common_transfers), 2)
        ships = all_transfers.filtered(
            lambda o: o.picking_type_id == warehouse.out_type_id
        )
        packs = all_transfers.filtered(
            lambda o: o.picking_type_id == warehouse.pack_type_id
        )
        picks = all_transfers.filtered(
            lambda o: o.picking_type_id == warehouse.pick_type_id
        )
        self.assertEqual(len(ships), 1)
        self.assertEqual(len(packs), 1)
        self.assertEqual(len(picks), 2)
        self.assertTrue(so1.picking_ids - so2.picking_ids)

    def test_delivery_multi_step_cancel_so1(self):
        """the warehouse uses pick + ship. Cancel SO1

        -> shippings are grouped, pickings are not"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        ships = so1.picking_ids & so2.picking_ids
        so1.action_cancel()
        self.assertEqual(ships.state, "waiting")
        pick1 = so1.picking_ids - ships
        self.assertEqual(pick1.state, "cancel")
        pick2 = so2.picking_ids - ships
        self.assertEqual(pick2.state, "confirmed")

    def test_delivery_multi_step_cancel_so2(self):
        """the warehouse uses pick + ship. Cancel SO2

        -> shippings are grouped, pickings are not"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        ships = so1.picking_ids & so2.picking_ids
        so2.action_cancel()
        self.assertEqual(ships.state, "waiting")
        pick1 = so1.picking_ids - ships
        self.assertEqual(pick1.state, "confirmed")
        pick2 = so2.picking_ids - ships
        self.assertEqual(pick2.state, "cancel")

    def test_delivery_multi_step_group_pick_cancel_so1(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> shippings are grouped, as well as pickings"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so1.action_cancel()
        # ship & pick should be shared between so1 and so2
        transfers = so1.picking_ids
        ship = transfers.filtered(lambda o: o.picking_type_id == warehouse.out_type_id)
        pick = transfers.filtered(lambda o: o.picking_type_id == warehouse.pick_type_id)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 1)
        self.assertEqual(ship.state, "waiting")
        self.assertEqual(pick.state, "confirmed")

    def test_delivery_multi_step_group_pick_cancel_so2(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> shippings are grouped, as well as pickings"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so2.action_cancel()
        # ship & pick should be shared between so1 and so2
        transfers = so1.picking_ids
        ship = transfers.filtered(lambda o: o.picking_type_id == warehouse.out_type_id)
        pick = transfers.filtered(lambda o: o.picking_type_id == warehouse.pick_type_id)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 1)
        self.assertEqual(ship.state, "waiting")
        self.assertEqual(pick.state, "confirmed")

    def test_delivery_multi_step_cancel_so1_create_so3(self):
        """the warehouse uses pick + ship. Cancel SO1, create SO3

        -> shippings are grouped, pickings are not"""
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        ships = so1.picking_ids & so2.picking_ids
        so1.action_cancel()
        so3 = self._get_new_sale_order(amount=12, carrier=self.carrier1)
        so3.action_confirm()
        self.assertTrue(ships in so3.picking_ids)
        pick3 = so3.picking_ids - ships
        self.assertEqual(len(pick3), 1)
        self.assertEqual(pick3.state, "confirmed")

    def test_delivery_mult_step_cancelling_sale_order1_before_create_order2(self):
        """1st sale order is cancelled

        -> picking is still todo with only 1 stock move todo"""
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so1.action_cancel()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_sale_stock_merge_procurement_group(self):
        """sale orders are merged, procurement groups are merged

        Ensure that the procurement group is linked with both SO
        and we find the stock.picking records from the SO.
        Ensure that printed transfers keep their procurement group.
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.name = "SO1"
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.name = "SO2"
        so1.action_confirm()
        so2.action_confirm()
        self.assertEqual(so1.picking_ids, so2.picking_ids)
        picking = so1.picking_ids
        # the group is the same on the move lines and picking
        self.assertEqual(picking.group_id, picking.move_lines.group_id)
        group = picking.group_id
        # the group is related to both sales orders
        self.assertEqual(group.sale_ids, so1 | so2)
        self.assertEqual(group.name, "{}, {}".format(so1.name, so2.name))

        self._update_qty_in_location(
            picking.location_id,
            so1.order_line.product_id,
            so1.order_line.product_uom_qty,
        )
        picking.action_assign()

        # process move of so1, we'll expect groups for new backorders and new
        # transfers merged in the backorder to "forget" about so1
        move1 = picking.move_lines.filtered(
            lambda line: line.sale_line_id.order_id == so1
        )
        line1 = move1.move_line_ids
        line1.qty_done = line1.product_uom_qty
        picking.action_done()

        backorder = picking.backorder_ids
        # as we no longer have anything of so1 in the backorder,
        # now it's only related to so2
        self.assertEqual(backorder.group_id.sale_ids, so2)
        self.assertEqual(backorder.group_id.name, so2.name)

        so3 = self._get_new_sale_order(carrier=self.carrier1)
        so3.name = "SO3"
        so3.action_confirm()

        # so3 moves are merged in the backorder used for so2,
        # a new group is used to hold so2 and so3
        self.assertEqual(backorder.group_id.sale_ids, so2 | so3)
        self.assertEqual(backorder.group_id.name, "{}, {}".format(so2.name, so3.name))

        self.assertEqual(so1.picking_ids, picking)
        self.assertEqual(so2.picking_ids, picking | backorder)
        self.assertEqual(so3.picking_ids, backorder)

    def test_create_backorder(self):
        """Ensure there is no regression when group pickings is disabled when
        we confirm a partial qty on a picking to create a backorder.
        """
        so = self._get_new_sale_order(amount=10, carrier=self.carrier1)
        so.name = "SO TEST"
        so.action_confirm()
        picking = so.picking_ids
        picking.picking_type_id.group_pickings = False
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
