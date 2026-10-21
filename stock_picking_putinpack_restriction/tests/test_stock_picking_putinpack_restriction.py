# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockPickingPutInPackRestriction(BaseCommon):
    # Package fields and buttons are only shown to package managers.
    _test_user_groups = (
        "stock.group_stock_manager",
        "stock.group_tracking_lot",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.picking_type = cls.warehouse.out_type_id
        cls.stock = cls.warehouse.lot_stock_id
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.stock,
            20,
        )
        cls.picking = cls._create_picking()
        cls.picking.action_confirm()
        cls.picking.action_assign()

    @classmethod
    def _create_picking(cls, qty=5.0):
        return cls.env["stock.picking"].create(
            {
                "location_id": cls.stock.id,
                "location_dest_id": cls.customers.id,
                "picking_type_id": cls.picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "location_id": cls.stock.id,
                            "location_dest_id": cls.customers.id,
                            "product_id": cls.product.id,
                            "product_uom_qty": qty,
                            "uom_id": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )

    def _set_picked(self, picking):
        picking.move_ids.picked = True

    def _msg_not_allowed(self):
        return re.escape(
            "Destination package can not be used with "
            f"{self.picking_type.name} transfer."
        )

    def _msg_done_no_package(self):
        return re.escape(
            "Using a package on transfer type "
            f"{self.picking_type.display_name} is not allowed."
        )

    def _msg_done_with_package(self):
        return re.escape(
            f"A package is required for transfer type {self.picking_type.display_name}."
        )

    # Field and view

    def test_selection_values(self):
        field = self.env["stock.picking.type"]._fields["put_in_pack_restriction"]
        values = [key for key, _label in field._description_selection(self.env)]
        self.assertEqual(values, ["no_package", "with_package"])

    def test_picking_related_field(self):
        self.assertFalse(self.picking.put_in_pack_restriction)
        self.picking_type.put_in_pack_restriction = "no_package"
        self.assertEqual(self.picking.put_in_pack_restriction, "no_package")

    def test_picking_form_view_hides_button(self):
        arch = self.env["stock.picking"].get_views([(False, "form")])["views"]["form"][
            "arch"
        ]
        self.assertIn("put_in_pack_restriction == 'no_package'", arch)

    def test_picking_type_form_view_has_field(self):
        arch = self.env["stock.picking.type"].get_views([(False, "form")])["views"][
            "form"
        ]["arch"]
        self.assertIn('name="put_in_pack_restriction"', arch)

    # Put in pack actions

    def test_put_in_pack_no_restriction(self):
        self._set_picked(self.picking)
        self.picking.action_put_in_pack()
        self.assertTrue(self.picking.move_line_ids.result_package_id)

    def test_put_in_pack_package_not_allowed(self):
        """Check put in pack is not allowed with no_package."""
        self.picking_type.put_in_pack_restriction = "no_package"
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            self.picking.action_put_in_pack()
        self.assertFalse(self.picking.move_line_ids.result_package_id)

    def test_put_in_pack_with_package_allowed(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self._set_picked(self.picking)
        self.picking.action_put_in_pack()
        self.assertTrue(self.picking.move_line_ids.result_package_id)

    def test_move_line_put_in_pack_not_allowed(self):
        self.picking_type.put_in_pack_restriction = "no_package"
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            self.picking.move_line_ids.action_put_in_pack()

    def test_move_line_put_in_pack_with_capacity_not_allowed(self):
        """The split by package capacity path must also be blocked."""
        self.picking_type.put_in_pack_restriction = "no_package"
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            self.picking.move_line_ids.action_put_in_pack(package_capacity=2)
        self.assertFalse(self.picking.move_line_ids.result_package_id)

    def test_move_line_put_in_pack_with_capacity_allowed(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self.picking.move_line_ids.action_put_in_pack(package_capacity=2)
        self.assertTrue(
            all(line.result_package_id for line in self.picking.move_line_ids)
        )

    def test_move_line_put_in_pack_all_move_line_ids_context(self):
        """Lines given in context 'all_move_line_ids' are checked too."""
        self.picking_type.put_in_pack_restriction = "no_package"
        other_type = self.warehouse.int_type_id
        self.assertFalse(other_type.put_in_pack_restriction)
        other_picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock.id,
                "location_dest_id": self.stock.id,
                "picking_type_id": other_type.id,
            }
        )
        other_line = self.env["stock.move.line"].create(
            {
                "picking_id": other_picking.id,
                "product_id": self.product.id,
                "location_id": self.stock.id,
                "location_dest_id": self.stock.id,
                "quantity": 1,
            }
        )
        lines = other_line.with_context(
            all_move_line_ids=self.picking.move_line_ids.ids
        )
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            lines.action_put_in_pack()

    def test_put_in_pack_wizard_not_allowed(self):
        """The put in pack wizard can not bypass the restriction."""
        self.picking_type.put_in_pack_restriction = "no_package"
        wizard = self.env["stock.put.in.pack"].create(
            {"move_line_ids": [Command.set(self.picking.move_line_ids.ids)]}
        )
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            wizard.action_put_in_pack()

    def test_package_put_in_pack_not_allowed(self):
        """Putting packages of the transfer into a parent package is blocked."""
        self._set_picked(self.picking)
        self.picking.action_put_in_pack()
        package = self.picking.move_line_ids.result_package_id
        self.assertTrue(package)
        self.picking_type.put_in_pack_restriction = "no_package"
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            package.action_put_in_pack()
        self.assertFalse(package.package_dest_id)

    def test_package_put_in_pack_allowed(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self._set_picked(self.picking)
        self.picking.action_put_in_pack()
        package = self.picking.move_line_ids.result_package_id
        package.action_put_in_pack()
        self.assertTrue(package.package_dest_id)

    def test_batch_put_in_pack_not_allowed(self):
        self.picking_type.put_in_pack_restriction = "no_package"
        batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(self.picking.ids)]}
        )
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            batch.action_put_in_pack()

    # Validation of the transfer

    def test_picking_done_breaks_restriction_with_package(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self.assertEqual(self.picking.state, "assigned")
        self._set_picked(self.picking)
        with self.assertRaisesRegex(ValidationError, self._msg_done_with_package()):
            self.picking._action_done()
        # Check it works without restriction
        self.picking_type.put_in_pack_restriction = False
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")

    def test_picking_done_with_package_after_put_in_pack(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self._set_picked(self.picking)
        self.picking.action_put_in_pack()
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")

    def test_picking_done_breaks_restriction_no_package(self):
        self.picking_type.put_in_pack_restriction = "no_package"
        self.assertEqual(self.picking.state, "assigned")
        self._set_picked(self.picking)
        self.picking.move_line_ids[0].result_package_id = self.env[
            "stock.package"
        ].create({})
        with self.assertRaisesRegex(ValidationError, self._msg_done_no_package()):
            self.picking._action_done()
        # Check it works without restriction
        self.picking_type.put_in_pack_restriction = False
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")

    def test_picking_done_no_package_without_package(self):
        self.picking_type.put_in_pack_restriction = "no_package"
        self._set_picked(self.picking)
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.picking.move_line_ids.result_package_id)

    def test_partial_picking_line_with_zero_qty(self):
        """Lines removed by the validation (zero quantity) are not checked."""
        self.picking_type.put_in_pack_restriction = "with_package"
        move = self.picking.move_ids
        move.quantity = 1
        move.picked = True
        new_move = self.env["stock.move"].create(move._split(4))
        self.assertEqual(new_move.quantity, 0)
        move.move_line_ids.result_package_id = self.env["stock.package"].create({})
        self.picking._action_done()
        self.assertEqual(move.state, "done")

    def test_backorder_with_package(self):
        """Partial validation with a package creates a valid backorder."""
        self.picking_type.put_in_pack_restriction = "with_package"
        move = self.picking.move_ids
        move.quantity = 3
        move.picked = True
        self.picking.action_put_in_pack()
        res = self.picking.button_validate()
        if isinstance(res, dict) and res.get("res_model"):
            wizard = (
                self.env[res["res_model"]].with_context(**res["context"]).create({})
            )
            wizard.process()
        self.assertEqual(self.picking.state, "done")
        backorder = self.picking.backorder_ids
        self.assertEqual(len(backorder), 1)
        self.assertEqual(backorder.put_in_pack_restriction, "with_package")
