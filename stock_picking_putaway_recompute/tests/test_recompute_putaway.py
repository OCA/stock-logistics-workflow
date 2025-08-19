# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command, first
from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestRecomputePutaway(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.rule_obj = cls.env["stock.putaway.rule"]
        cls.location_obj = cls.env["stock.location"]
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.type_in = cls.env.ref("stock.picking_type_in")
        cls.type_in.allow_to_recompute_putaways = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test product 2",
            }
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
        # Create the same rule for product 2
        cls.rule_2 = cls.rule_obj.create(
            {
                "product_id": cls.product_2.id,
                "location_in_id": cls.stock.id,
                "location_out_id": cls.sub_location_1.id,
            }
        )

        cls.package = cls.env["stock.quant.package"].create({})

    def _create_picking(self):
        self.picking = self.env["stock.picking"].create(
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
                    ),
                    Command.create(
                        {
                            "location_id": self.suppliers.id,
                            "location_dest_id": self.stock.id,
                            "name": self.product.name,
                            "product_id": self.product_2.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                ],
            }
        )
        return self.picking

    def test_recompute_putaway(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Change the rule to point to Sub location 2
        Launch the acdtion to recompute putaways
        The operation point to the Sub location 2
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.action_recompute_putaways()

        self.assertEqual(
            self.sub_location_2, first(self.picking.move_line_ids).location_dest_id
        )

    def test_recompute_putaway_line(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Change the rule to point to Sub location 2
        Launch the action to recompute putaways on line level
        The operation point to the Sub location 2
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.move_line_ids.action_recompute_putaways()

        self.assertEqual(
            self.sub_location_2, first(self.picking.move_line_ids).location_dest_id
        )

    def test_recompute_putaway_qty_done(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Fill in a quantity to qty_done
        Change the rule to point to Sub location 2
        Launch the acdtion to recompute putaways
        The operation point still to the Sub location 1
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        self.picking.move_line_ids.picked = True
        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.action_recompute_putaways()

        # destination location should remain the same
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

    def test_recompute_putaway_printed(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Set the picking as printed
        Change the rule to point to Sub location 2
        Launch the acdtion to recompute putaways
        The operation point still to the Sub location 1
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        self.picking.printed = True
        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.action_recompute_putaways()

        # destination location should remain the same
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

    def test_can_recompute(self):
        """
        Create a two pickings from Suppliers -> Stock
        The visibility of the Recompute button is enabled for both
        Set the picking 1 as printed
        The visibility of the Recompute button is enabled for picking 2 only
        """
        picking1 = self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.can_recompute_putaways)

        picking2 = self._create_picking()
        self.picking.action_confirm()
        pickings = picking1 | picking2
        self.assertEqual([True, True], pickings.mapped("can_recompute_putaways"))

        picking1.printed = True
        self.assertEqual([False, True], pickings.mapped("can_recompute_putaways"))

    def test_line_can_recompute(self):
        """
        Create a two pickings from Suppliers -> Stock
        The visibility of the Recompute button is enabled for both
        Set the picking 1 as printed
        The visibility of the Recompute button is enabled for picking 2 only
        """
        picking1 = self._create_picking()
        self.picking.action_confirm()

        self.assertEqual(
            [True, True], self.picking.move_line_ids.mapped("can_recompute_putaways")
        )

        picking2 = self._create_picking()
        self.picking.action_confirm()
        move_lines_picking1 = picking1.move_line_ids
        self.assertEqual(
            [True, True], move_lines_picking1.mapped("can_recompute_putaways")
        )

        move_lines_picking2 = picking2.move_line_ids
        self.assertEqual(
            [True, True], move_lines_picking2.mapped("can_recompute_putaways")
        )

        picking1.printed = True
        move_lines_picking1 = picking1.move_line_ids
        self.assertEqual(
            [False, False], move_lines_picking1.mapped("can_recompute_putaways")
        )
        move_lines_picking2 = picking2.move_line_ids
        self.assertEqual(
            [True, True], move_lines_picking2.mapped("can_recompute_putaways")
        )

        picking1.printed = False
        picking2.move_line_ids.picked = True
        move_lines_picking1 = picking1.move_line_ids
        self.assertEqual(
            [True, True], move_lines_picking1.mapped("can_recompute_putaways")
        )
        move_lines_picking2 = picking2.move_line_ids
        self.assertEqual(
            [False, False], move_lines_picking2.mapped("can_recompute_putaways")
        )

    def test_recompute_putaway_packaging(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Simulate a package presence on operations
        Change the rule to point to Sub location 2
        Launch the action to recompute putaways
        The operation still points to the Sub location 1
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        # Simulate the package is already set
        self.picking.move_line_ids.result_package_id = self.package

        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.action_recompute_putaways()

        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

    def test_no_recompute_putaway(self):
        """
        Create a single picking from Suppliers -> Stock
        The created operation point to the Sub location 1
        Deactivate the option on picking type level
        Change the rule to point to Sub location 2
        Launch the action to recompute putaways
        The operation still points to the Sub location 1
        """
        self._create_picking()
        self.picking.action_confirm()

        self.assertTrue(self.picking.move_line_ids)
        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )

        # Simulate the package is already set
        self.type_in.allow_to_recompute_putaways = False

        # Change the rule destination
        self.rule.location_out_id = self.sub_location_2

        self.picking.action_recompute_putaways()

        self.assertEqual(
            self.sub_location_1, self.picking.move_line_ids.location_dest_id
        )
