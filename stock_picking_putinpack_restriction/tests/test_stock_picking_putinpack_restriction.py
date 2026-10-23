# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingPutInPackRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
    def _create_picking(cls, picking_type=None, qty=5.0):
        picking_type = picking_type or cls.picking_type
        return cls.env["stock.picking"].create(
            {
                "location_id": cls.stock.id,
                "location_dest_id": cls.customers.id,
                "picking_type_id": picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "location_id": cls.stock.id,
                            "location_dest_id": cls.customers.id,
                            "product_id": cls.product.id,
                            "product_uom_qty": qty,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )

    def _set_picked(self, picking):
        picking.move_ids.picked = True

    def _msg_not_allowed(self, name=None):
        return re.escape(
            "Destination package can not be used with "
            f"{name or self.picking_type.name} transfer."
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

    def _enable_packages(self):
        # Package fields and buttons are only shown to package managers.
        self.env.user.groups_id += self.env.ref("stock.group_tracking_lot")

    # Field and views

    def test_picking_related_field(self):
        self.assertFalse(self.picking.put_in_pack_restriction)
        self.picking_type.put_in_pack_restriction = "no_package"
        self.assertEqual(self.picking.put_in_pack_restriction, "no_package")

    def test_picking_form_view_hides_button(self):
        self._enable_packages()
        arch = self.env["stock.picking"].get_views([(False, "form")])["views"]["form"][
            "arch"
        ]
        self.assertIn("put_in_pack_restriction == 'no_package'", arch)

    def test_picking_type_form_view_has_field(self):
        self._enable_packages()
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
        self.assertFalse(self.picking.move_line_ids.result_package_id)

    def test_pre_put_in_pack_hook_checks_move_line_pickings(self):
        """Move lines from another transfer (as in a batch) are checked too."""
        self.picking_type.put_in_pack_restriction = "no_package"
        other_type = self.warehouse.pick_type_id
        self.assertFalse(other_type.put_in_pack_restriction)
        other_picking = self._create_picking(picking_type=other_type)
        with self.assertRaisesRegex(ValidationError, self._msg_not_allowed()):
            other_picking._pre_put_in_pack_hook(
                other_picking.move_line_ids | self.picking.move_line_ids
            )

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
            "stock.quant.package"
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
        move.move_line_ids.result_package_id = self.env["stock.quant.package"].create(
            {}
        )
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
