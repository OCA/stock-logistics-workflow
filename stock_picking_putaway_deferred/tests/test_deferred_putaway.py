# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestDeferredPutaway(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_obj = cls.env["stock.putaway.rule"]
        cls.location_obj = cls.env["stock.location"]
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.type_in = cls.env.ref("stock.picking_type_in")
        cls.type_in.write(
            {
                "defer_putaway_to_operator": True,
                "allow_to_recompute_putaways": True,
            }
        )
        cls.type_int = cls.env.ref("stock.picking_type_internal")
        cls.type_int.write(
            {
                "defer_putaway_to_operator": True,
                "allow_to_recompute_putaways": True,
            }
        )

        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "product"}
        )
        cls.sub_location_1 = cls.location_obj.create(
            {
                "name": "Sub location 1",
                "location_id": cls.stock.id,
                "usage": "internal",
            }
        )
        cls.sub_location_2 = cls.location_obj.create(
            {
                "name": "Sub location 2",
                "location_id": cls.stock.id,
                "usage": "internal",
            }
        )
        cls.rule = cls.rule_obj.create(
            {
                "product_id": cls.product.id,
                "location_in_id": cls.stock.id,
                "location_out_id": cls.sub_location_1.id,
            }
        )
        # Add a putaway rule for product_2 pointing to sub_location_2
        cls.rule_2 = cls.rule_obj.create(
            {
                "product_id": cls.product_2.id,
                "location_in_id": cls.stock.id,
                "location_out_id": cls.sub_location_2.id,
            }
        )

    def _create_picking(self):
        """
        Helper: create a picking with a single move for self.product, 10 units,
        from suppliers to stock.  Returns the picking.
        """
        return self.env["stock.picking"].create(
            {
                "location_id": self.suppliers.id,
                "location_dest_id": self.stock.id,
                "picking_type_id": self.type_in.id,
                "move_ids": [
                    Command.create(
                        {
                            "location_id": self.suppliers.id,
                            "location_dest_id": self.stock.id,
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 10.0,
                        }
                    )
                ],
            }
        )

    def _create_whole_package_picking(self):
        """
        Helper: create an internal transfer that reserves ALL quants of a package
        so that Odoo auto-creates a package_level (via _check_entire_pack).
        Returns (picking, line1, line2, package) where line1 is for product and
        line2 is for product_2.
        """
        package = self.env["stock.quant.package"].create({"name": "TEST-WHOLE-PKG"})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.sub_location_2, 10.0, package_id=package
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_2, self.sub_location_2, 10.0, package_id=package
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.type_int.id,
                "location_id": self.sub_location_2.id,
                "location_dest_id": self.stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 10.0,
                            "location_id": self.sub_location_2.id,
                            "location_dest_id": self.stock.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": self.product_2.name,
                            "product_id": self.product_2.id,
                            "product_uom": self.product_2.uom_id.id,
                            "product_uom_qty": 10.0,
                            "location_id": self.sub_location_2.id,
                            "location_dest_id": self.stock.id,
                        }
                    ),
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        line1 = picking.move_line_ids.filtered(lambda ml: ml.product_id == self.product)
        line2 = picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )
        return picking, line1, line2, package

    def _create_package_level_picking(self, products_and_qty):
        """
        Helper: create a picking with package_level_ids created directly (the
        natural "move entire package" workflow).  Odoo generates moves from the
        package quants during action_confirm() via package_level._generate_moves().

        products_and_qty: list of (product, qty) to seed into the package.
        Returns (picking, package_level).
        """
        package = self.env["stock.quant.package"].create(
            {"name": "TEST-PKG-LEVEL-DIRECT"}
        )
        for product, qty in products_and_qty:
            self.env["stock.quant"]._update_available_quantity(
                product, self.sub_location_2, qty, package_id=package
            )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.type_int.id,
                "location_id": self.sub_location_2.id,
                "location_dest_id": self.stock.id,
                "package_level_ids": [
                    Command.create(
                        {
                            "package_id": package.id,
                            "company_id": self.type_int.company_id.id,
                        }
                    )
                ],
            }
        )
        # action_confirm generates moves from package quants (via _generate_moves);
        # action_assign reserves stock and creates move lines.
        picking.action_confirm()
        picking.action_assign()
        return picking, picking.package_level_ids

    def test_putaway_not_applied_at_assign(self):
        """
        After reservation, lines of a deferred picking type should:
        - have location_dest_id equal to the move destination (putaway not applied)
        - have putaway_deferred = True
        """
        picking = self._create_picking()
        picking.action_confirm()
        self.assertTrue(picking.move_line_ids)
        line = picking.move_line_ids
        self.assertEqual(line.location_dest_id, self.stock)
        self.assertTrue(line.putaway_deferred)
        self.assertTrue(picking.putaway_pending)
        self.assertTrue(picking.can_recompute_putaways)

    def test_apply_putaway_manually(self):
        """
        After calling action_recompute_putaways, putaway should be applied:
        - location_dest_id becomes the sub-location from the rule
        - putaway_deferred cleared, putaway_pending False
        """
        picking = self._create_picking()
        picking.action_confirm()
        picking.action_recompute_putaways()
        line = picking.move_line_ids
        self.assertEqual(line.location_dest_id, self.sub_location_1)
        self.assertFalse(line.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_action_done_blocked_when_putaway_pending(self):
        """
        _action_done on move lines raises UserError if putaway is still deferred.
        The check fires at operation execution level, not at picking validation.
        """
        picking = self._create_picking()
        picking.action_confirm()
        with self.assertRaises(UserError):
            picking.move_line_ids._action_done()

    def test_validate_allowed_after_putaway_applied(self):
        """
        Validation proceeds normally once putaway has been applied.
        """
        picking = self._create_picking()
        picking.action_confirm()
        picking.action_recompute_putaways()
        picking.move_line_ids.qty_done = 10.0
        # Should not raise
        picking.button_validate()

    def test_can_apply_putaway_when_printed(self):
        """
        For deferred pickings, the recompute button must remain available
        even after the picking is printed (unlike the standard recompute flow).
        """
        picking = self._create_picking()
        picking.action_confirm()
        picking.printed = True
        self.assertTrue(picking.can_recompute_putaways)
        # Putaway application should work
        picking.action_recompute_putaways()
        self.assertFalse(picking.putaway_pending)

    def test_non_deferred_picking_type_unaffected(self):
        """
        A picking type without defer_putaway_to_operator behaves as before:
        putaway is applied at reservation, putaway_deferred stays False.
        """
        self.type_in.defer_putaway_to_operator = False
        try:
            picking = self._create_picking()
            picking.action_confirm()
            line = picking.move_line_ids
            self.assertEqual(line.location_dest_id, self.sub_location_1)
            self.assertFalse(line.putaway_deferred)
            self.assertFalse(picking.putaway_pending)
        finally:
            self.type_in.defer_putaway_to_operator = True

    def test_putaway_deferred_only_for_new_lines_on_reassign(self):
        """
        On re-assign (partial reservation completed), only newly created lines
        should be marked deferred; previously processed lines keep their state.
        """
        picking = self._create_picking()
        picking.action_confirm()
        line = picking.move_line_ids
        self.assertTrue(line.putaway_deferred)
        # Simulate operator applied putaway
        picking.action_recompute_putaways()
        self.assertFalse(line.putaway_deferred)
        self.assertEqual(line.location_dest_id, self.sub_location_1)
        # Re-assign should not reset the already-applied line
        picking.action_assign()
        self.assertFalse(line.putaway_deferred)

    def test_operator_sets_location_manually(self):
        """
        If the operator manually sets location_dest_id on a deferred move line,
        putaway_deferred is cleared: the explicit destination choice is sufficient
        and _action_done must not block.
        """
        picking = self._create_picking()
        picking.action_confirm()
        line = picking.move_line_ids
        self.assertTrue(line.putaway_deferred)
        # Operator types in the destination directly
        line.location_dest_id = self.sub_location_2
        self.assertFalse(line.putaway_deferred)
        self.assertFalse(picking.putaway_pending)
        # The "Recompute Putaways" button is still available
        # since the picking is not yet printed
        self.assertTrue(picking.can_recompute_putaways)

    def test_unreserve_and_reassign_requires_putaway_again(self):
        """
        After putaway has been applied, unreserving then re-reserving creates
        fresh move lines: putaway must be applied again before processing.
        """
        picking = self._create_picking()
        picking.action_confirm()
        # Putaway deferred at reservation
        self.assertTrue(picking.move_line_ids.mapped("putaway_deferred"))
        # Operator applies putaway
        picking.action_recompute_putaways()
        self.assertFalse(picking.putaway_pending)
        self.assertEqual(picking.move_line_ids.location_dest_id, self.sub_location_1)
        # Unreserve: move lines are cleared
        picking.do_unreserve()
        self.assertFalse(picking.move_line_ids)
        # Re-reserve: new move lines created, putaway must be applied again
        picking.action_assign()
        self.assertTrue(picking.move_line_ids)
        self.assertTrue(picking.putaway_pending)
        self.assertTrue(all(picking.move_line_ids.mapped("putaway_deferred")))
        self.assertEqual(picking.move_line_ids.location_dest_id, self.stock)
        self.assertTrue(picking.can_recompute_putaways)

    def test_putaway_deferred_with_packaged_product(self):
        """
        When a product stored in a package is reserved for an internal transfer,
        the move line carries package_id (source package).
        The deferred putaway mechanism must still apply:
        - putaway_deferred is True right after reservation
        - action_recompute_putaways applies the rule and clears the flag
        """
        type_int = self.env.ref("stock.picking_type_internal")
        type_int.write(
            {
                "defer_putaway_to_operator": True,
                "allow_to_recompute_putaways": True,
            }
        )
        # Product in a package sitting in sub_location_2
        package = self.env["stock.quant.package"].create({"name": "TEST-PKG"})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.sub_location_2, 10.0, package_id=package
        )
        # Internal transfer
        # sub_location_2 -> stock; existing rule stock -> sub_location_1 applies
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": type_int.id,
                "location_id": self.sub_location_2.id,
                "location_dest_id": self.stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.sub_location_2.id,
                            "location_dest_id": self.stock.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()

        self.assertTrue(picking.move_line_ids)
        line = picking.move_line_ids

        # Source package must be tracked on the line
        self.assertEqual(line.package_id, package)
        # Putaway deferred despite the source package being set
        self.assertEqual(line.location_dest_id, self.stock)
        self.assertTrue(line.putaway_deferred)
        self.assertTrue(picking.putaway_pending)
        self.assertTrue(picking.can_recompute_putaways)

        # Apply putaway manually: existing rule stock -> sub_location_1 fires
        picking.action_recompute_putaways()
        self.assertEqual(line.location_dest_id, self.sub_location_1)
        self.assertFalse(line.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_putaway_deferred_with_packaged_products(self):
        """
        When two products stored in the same source package are reserved for a
        partial internal transfer (not a whole-package move), each move line gets
        its own deferred putaway applied independently:
        - both lines carry package_id (source package)
        - both lines are deferred at reservation time
        - action_recompute_putaways applies each product's rule independently
        - the shared source package does not constrain destination choices

        Note: partial quantities prevent Odoo from creating a package_level, so
        lines have result_package_id = False and are treated individually.
        """
        type_int = self.env.ref("stock.picking_type_internal")
        type_int.write(
            {
                "defer_putaway_to_operator": True,
                "allow_to_recompute_putaways": True,
            }
        )

        # Both products in the same source package at sub_location_2
        package = self.env["stock.quant.package"].create({"name": "TEST-PKG-MULTI"})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.sub_location_2, 10.0, package_id=package
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_2, self.sub_location_2, 10.0, package_id=package
        )
        # Partial transfer (5 of 10 each) -> no package_level created by Odoo;
        # destination stock; rules: product->sub_location_1, product_2->sub_location_2
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": type_int.id,
                "location_id": self.sub_location_2.id,
                "location_dest_id": self.stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.sub_location_2.id,
                            "location_dest_id": self.stock.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": self.product_2.name,
                            "product_id": self.product_2.id,
                            "product_uom": self.product_2.uom_id.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.sub_location_2.id,
                            "location_dest_id": self.stock.id,
                        }
                    ),
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()

        self.assertEqual(len(picking.move_line_ids), 2)
        line1 = picking.move_line_ids.filtered(lambda ml: ml.product_id == self.product)
        line2 = picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )

        # Both lines reference the same source package
        self.assertEqual(line1.package_id, package)
        self.assertEqual(line2.package_id, package)
        # No result_package_id: partial transfer, items leave the source package
        self.assertFalse(line1.result_package_id)
        self.assertFalse(line2.result_package_id)
        # Putaway deferred on both lines despite the shared source package
        self.assertEqual(line1.location_dest_id, self.stock)
        self.assertEqual(line2.location_dest_id, self.stock)
        self.assertTrue(line1.putaway_deferred)
        self.assertTrue(line2.putaway_deferred)
        self.assertTrue(picking.putaway_pending)
        self.assertTrue(picking.can_recompute_putaways)

        # Apply putaway: each product's rule fires independently
        picking.action_recompute_putaways()
        # product -> sub_location_1 (existing rule)
        self.assertEqual(line1.location_dest_id, self.sub_location_1)
        # product_2 -> sub_location_2 (rule added above)
        self.assertEqual(line2.location_dest_id, self.sub_location_2)
        self.assertFalse(line1.putaway_deferred)
        self.assertFalse(line2.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_can_recompute_putaways_field(self):
        """
        can_recompute_putaways is True for deferred assigned pickings regardless
        of allow_to_recompute_putaways on the picking type.
        """
        picking = self._create_picking()
        picking.action_confirm()
        self.assertTrue(picking.can_recompute_putaways)
        # Even with allow_to_recompute_putaways disabled, deferred pickings
        # still expose the button
        self.type_in.allow_to_recompute_putaways = False
        picking.invalidate_recordset(["can_recompute_putaways"])
        self.assertTrue(picking.can_recompute_putaways)
        self.type_in.allow_to_recompute_putaways = True

    def test_whole_package_move_putaway_deferred_single_product_rule(self):
        """
        When ALL quants of a package are reserved, Odoo auto-creates a package_level
        (via _check_entire_pack) and sets result_package_id on the move lines.
        The defer mechanism still applies because package_level_id is also set
        (lines with result_package_id AND package_level_id are NOT excluded from deferral).

        With a single non-conflicting product rule the putaway fires correctly:
        the package (and both lines) end up at the putaway location.
        """
        # product_2 gets the SAME destination as product to avoid the conflict fallback
        self.rule_2.location_out_id = self.sub_location_1

        picking, line1, line2, package = self._create_whole_package_picking()

        # Odoo must have created a package_level covering the whole package
        self.assertTrue(picking.package_level_ids)
        package_level = picking.package_level_ids
        self.assertEqual(package_level.package_id, package)

        # Both lines carry result_package_id (disposable package) and package_level_id
        self.assertEqual(line1.result_package_id, package)
        self.assertEqual(line2.result_package_id, package)
        self.assertTrue(line1.package_level_id)
        self.assertTrue(line2.package_level_id)

        # Putaway is deferred on both lines
        self.assertTrue(line1.putaway_deferred)
        self.assertTrue(line2.putaway_deferred)
        self.assertEqual(line1.location_dest_id, self.stock)
        self.assertEqual(line2.location_dest_id, self.stock)
        self.assertTrue(picking.putaway_pending)

        # Both products have the same putaway destination -> no conflict
        picking.action_recompute_putaways()
        self.assertEqual(line1.location_dest_id, self.sub_location_1)
        self.assertEqual(line2.location_dest_id, self.sub_location_1)
        self.assertEqual(package_level.location_dest_id, self.sub_location_1)
        self.assertFalse(line1.putaway_deferred)
        self.assertFalse(line2.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_whole_package_move_putaway_conflict_falls_back_to_default(self):
        """
        When ALL quants of a package are reserved, Odoo auto-creates a package_level.
        A package can only go to ONE location, so if individual product putaway rules
        would send the products to different locations, _apply_putaway_strategy falls
        back to the move's destination (the 'elif package' branch in Odoo core).

        This is correct behaviour: the operator must manually choose the destination
        of the package level when the automatic rules conflict.
        """
        # product -> sub_location_1, product_2 -> sub_location_2 (conflict)

        picking, line1, line2, package = self._create_whole_package_picking()

        # Odoo created a package_level
        self.assertTrue(picking.package_level_ids)
        # Putaway deferred on both lines
        self.assertTrue(line1.putaway_deferred)
        self.assertTrue(line2.putaway_deferred)

        # Recompute: conflicting rules -> _apply_putaway_strategy falls back to
        # the move's destination; the package cannot be split across locations
        picking.action_recompute_putaways()
        self.assertEqual(line1.location_dest_id, self.stock)
        self.assertEqual(line2.location_dest_id, self.stock)
        self.assertEqual(picking.package_level_ids.location_dest_id, self.stock)
        # Flag cleared: putaway was processed, operator must adjust manually if needed
        self.assertFalse(line1.putaway_deferred)
        self.assertFalse(line2.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_package_level_single_product_putaway_deferred(self):
        """
        Creating a picking with a package_level directly (1 product in package):
        - action_confirm generates 1 move via _generate_moves
        - action_assign reserves stock -> 1 move line linked to the package_level
        - defer mechanism marks the line as putaway_deferred
        - action_recompute_putaways applies the product rule -> sub_location_1
        - package_level.location_dest_id is updated to sub_location_1
        """
        picking, package_level = self._create_package_level_picking(
            [(self.product, 10.0)]
        )

        self.assertEqual(len(package_level), 1)
        self.assertEqual(len(picking.move_line_ids), 1)
        line = picking.move_line_ids

        # The move line must be linked to the package level
        self.assertTrue(line.package_level_id)
        self.assertEqual(line.package_level_id, package_level)

        # Defer mechanism active: location stays at move destination
        self.assertTrue(line.putaway_deferred)
        self.assertEqual(line.location_dest_id, self.stock)
        self.assertTrue(picking.putaway_pending)

        # Recompute: product rule sends to sub_location_1 (no conflict)
        picking.action_recompute_putaways()
        self.assertEqual(line.location_dest_id, self.sub_location_1)
        self.assertEqual(package_level.location_dest_id, self.sub_location_1)
        self.assertFalse(line.putaway_deferred)
        self.assertFalse(picking.putaway_pending)

    def test_package_level_two_products_putaway_deferred(self):
        """
        Creating a picking with a package_level directly (2 products in package):
        - action_confirm generates 2 moves via _generate_moves
        - action_assign reserves -> 2 move lines sharing the same package_level
        - defer mechanism marks both lines as putaway_deferred
        - With consistent putaway rules (both -> sub_location_1), recompute succeeds:
          both lines and the package_level end up at sub_location_1
        """
        self.rule_2.location_out_id = self.sub_location_1

        picking, package_level = self._create_package_level_picking(
            [(self.product, 10.0), (self.product_2, 10.0)]
        )

        self.assertEqual(len(package_level), 1)
        self.assertEqual(len(picking.move_line_ids), 2)

        line1 = picking.move_line_ids.filtered(lambda ml: ml.product_id == self.product)
        line2 = picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )

        # Both lines share the same package level
        self.assertEqual(line1.package_level_id, package_level)
        self.assertEqual(line2.package_level_id, package_level)

        # Defer mechanism active on both lines
        self.assertTrue(line1.putaway_deferred)
        self.assertTrue(line2.putaway_deferred)
        self.assertEqual(line1.location_dest_id, self.stock)
        self.assertEqual(line2.location_dest_id, self.stock)
        self.assertTrue(picking.putaway_pending)

        # Recompute: both products -> sub_location_1 (consistent, no conflict)
        picking.action_recompute_putaways()
        self.assertEqual(line1.location_dest_id, self.sub_location_1)
        self.assertEqual(line2.location_dest_id, self.sub_location_1)
        self.assertEqual(package_level.location_dest_id, self.sub_location_1)
        self.assertFalse(line1.putaway_deferred)
        self.assertFalse(line2.putaway_deferred)
        self.assertFalse(picking.putaway_pending)
