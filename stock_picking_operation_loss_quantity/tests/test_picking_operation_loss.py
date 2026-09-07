# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError

from .common import OperationLossQuantityCommon


class TestQuantityLoss(OperationLossQuantityCommon):
    def test_check_is_allowed_config(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_2.qty_done = 1.0

        # Unset the Warehouse global config
        self.warehouse.use_loss_picking = False
        with self.assertRaises(UserError):
            line_2.action_lose_quantity()

    def test_check_is_allowed_done(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)

        # Transfer the whole picking
        for line in self.picking_2.move_line_ids:
            line.qty_done = line.reserved_uom_qty
        self.picking_2._action_done()
        with self.assertRaises(UserError):
            line_2.action_lose_quantity()

    def test_initiate_values_no_tracking_initial_situation(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        self.assertEqual(len(lines), 2)
        line_p2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_p3 = lines.filtered(lambda line: line.product_id == self.product_3)
        self.assertEqual(line_p2.reserved_uom_qty, 6)
        self.assertEqual(line_p3.reserved_uom_qty, 2)

    def test_loss_line_no_tracking(self):
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        quants_available_quantity_line_2_before = self._get_quants_available_qty(line_2)

        line_2.action_lose_quantity()

        quants_available_quantity_line_2_after = self._get_quants_available_qty(line_2)

        self.assertEqual(quants_available_quantity_line_2_after, 0)
        self.assertEqual(quants_available_quantity_line_2_before, 4)

        self.assertEqual(line_2.reserved_qty, 1.0)
        self.assertEqual(line_2.qty_done, line_2.reserved_uom_qty)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        lock_moves = loss_pickings.move_ids.filtered("quant_lock_quant_id")
        self.assertTrue(lock_moves)
        self.assertEqual(line_2.product_id, lock_moves[0].product_id)

    def test_loss_line_no_tracking_multi(self):
        """
        Declare a loss quantity on both lines - this is not common
        through interface but can be done programmatically
        """
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        lines.action_lose_quantity()

        for line in lines:
            self.assertEqual(line.reserved_qty, 1.0)
            self.assertEqual(line.qty_done, line.reserved_qty)

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(1, len(loss_pickings))
        self.assertTrue(loss_pickings.move_ids.filtered("quant_lock_quant_id"))

    def test_loss_line_no_tracking_with_pack(self):
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 2.0

        self.picking_2._put_in_pack(line_2 | line_3)
        line_2_pack = self.picking_2.move_line_ids.filtered(
            lambda line: line.result_package_id and line.product_id == self.product_2
        )
        line_3_pack = self.picking_2.move_line_ids.filtered(
            lambda line: line.result_package_id and line.product_id == self.product_3
        )

        # Line 2 does not contain anymore a qty_done after put in pack
        # And a new line with the result package has been created
        self.assertEqual(len(self.picking_2.move_line_ids), 3)
        self.assertNotEqual(line_2, line_2_pack)
        self.assertEqual(line_2.qty_done, 0)
        self.assertEqual(line_2.reserved_qty, 5)
        self.assertEqual(line_3, line_3_pack)

        line_2.action_lose_quantity()

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(1, len(loss_pickings))
        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
        )
        self.assertFalse(line)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        )
        self.assertTrue(line)

        self.assertEqual(line.state, "assigned")
        self.assertEqual(line.reserved_uom_qty, 9)

    def test_unreserve_unprocessed_qty_converts_to_move_uom(self):
        """`_unreserve_unprocessed_qty` must return the freed quantity
        expressed in the move's UoM, not the move line's own UoM: it is
        summed and compared against `move.product_uom` in `_lose_quantity`.
        """
        dozen = self.env.ref("uom.product_uom_dozen")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": "Test move",
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 12,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move._action_confirm()
        self._create_quantities(self.product_2, 12.0)
        picking.action_assign()

        line = move.move_line_ids
        self.assertEqual(line.reserved_uom_qty, 12.0)

        # Switch the line to a coarser UoM of the same category (1 dozen ==
        # 12 units), keeping the same physical reserved quantity, then mark
        # a quarter of it as done.
        line.write({"product_uom_id": dozen.id, "reserved_uom_qty": 1.0})
        line.qty_done = 0.25

        unprocessed_qty = line._unreserve_unprocessed_qty()

        # 0.75 dozen unprocessed, converted to the move's UoM (units): 9.0,
        # not 0.75.
        self.assertEqual(unprocessed_qty, 9.0)
        self.assertEqual(line.reserved_uom_qty, 0.25)

    def test_lose_quantity_does_not_touch_quants_in_child_location(self):
        """`_lose_quantity` must only lock the exact quant behind the move
        line being declared as lost (`_gather(..., strict=True)`), never a
        quant that merely lives in a child of that location: `_gather`
        without `strict` matches locations `child_of` the one requested, so
        it would wrongly pick up unrelated stock stored in a sub-location.
        """
        shelf = self.env["stock.location"].create(
            {
                "name": "Shelf",
                "usage": "internal",
                "location_id": self.loc_stock.id,
            }
        )
        # Only loc_stock has stock at assignment time: the reservation is
        # deterministically made there, not on the (still empty) shelf.
        self._create_quantities(self.product_2, 5.0, location=self.loc_stock)

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": "Test move",
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 5,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move._action_confirm()
        picking.action_assign()

        line = move.move_line_ids
        self.assertEqual(line.location_id, self.loc_stock)
        line.qty_done = 2.0

        # Unrelated stock, added after the reservation, in a child location.
        self._create_quantities(self.product_2, 3.0, location=shelf)

        # Without `strict=True`, `_gather` would also match the shelf quant
        # (child of loc_stock) and lock it too, even though the line was
        # never reserved on it.
        line.action_lose_quantity()

        loc_stock_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", self.loc_stock.id),
            ]
        )
        # The quant actually behind the move line is the one locked...
        self.assertTrue(loc_stock_quant.is_locked_by_picking)
        self.assertEqual(
            loc_stock_quant.lock_move_ids.quant_lock_quant_id, loc_stock_quant
        )
        # ...the unrelated shelf quant is left alone by the locking itself
        shelf_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", shelf.id),
            ]
        )
        self.assertFalse(shelf_quant.is_locked_by_picking)

    def test_lose_quantity_does_not_touch_quants_of_another_owner(self):
        """`_lose_quantity` must only lock the exact quant behind the move
        line being declared as lost, never a quant of another owner:
        `_gather` without `strict` does not filter on `owner_id` at all when
        the line itself has none set, so it would wrongly pick up stock
        owned by someone else.
        """
        owner = self.env["res.partner"].create({"name": "Another owner"})
        # Only the un-owned stock exists at assignment time: the reservation
        # is deterministically made on it.
        self._create_quantities(self.product_2, 5.0)

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": "Test move",
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 5,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        move._action_confirm()
        picking.action_assign()

        line = move.move_line_ids
        self.assertFalse(line.owner_id)
        line.qty_done = 2.0

        # Unrelated stock, added after the reservation, owned by a partner.
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product_2.id,
                "inventory_quantity": 3.0,
                "location_id": self.loc_stock.id,
                "owner_id": owner.id,
            }
        )._apply_inventory()

        # Without `strict=True`, `_gather` would also match the owned quant
        # (the owner filter is only applied when the line itself has one)
        # and lock it too, even though the line was never reserved on it.
        line.action_lose_quantity()

        unowned_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", self.loc_stock.id),
                ("owner_id", "=", False),
            ]
        )
        owned_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_id", "=", self.loc_stock.id),
                ("owner_id", "=", owner.id),
            ]
        )
        self.assertTrue(unowned_quant.is_locked_by_picking)
        self.assertFalse(owned_quant.is_locked_by_picking)
