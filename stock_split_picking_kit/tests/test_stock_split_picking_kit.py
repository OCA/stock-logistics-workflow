# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import Form, SavepointCase


class TestStockSplitPickingKit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product_model = cls.env["product.product"]

        cls.product_garden_table = cls.product_model.create(
            {
                "name": "GARDEN TABLE",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
            }
        )
        cls.tmpl_garden_table = cls.product_garden_table.product_tmpl_id
        cls.product_garden_table_top = cls.product_model.create(
            {
                "name": "GARDEN TABLE TOP",
                "type": "product",
                "sale_ok": True,
            }
        )
        cls.product_garden_table_leg = cls.product_model.create(
            {
                "name": "GARDEN TABLE LEG",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.bom_model = cls.env["mrp.bom"]
        cls.bom_garden_table = cls.bom_model.create(
            {
                "product_tmpl_id": cls.tmpl_garden_table.id,
                "product_id": cls.product_garden_table.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_leg.id,
                            "product_qty": 4.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_top.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )

    @classmethod
    def _create_picking(cls, lines):
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.picking_type
        picking_form.partner_id = cls.partner
        for product, qty in lines:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.product_uom_qty = qty
        picking = picking_form.save()
        picking.action_confirm()
        return picking

    def _get_picking_ids_from_action(self, res, expected_quantity):
        """Return the new picking found in the action returned by the wizard."""
        id_list = res["domain"][0][2]
        self.assertEqual(len(id_list), expected_quantity)
        return self.env["stock.picking"].browse(id_list)

    @classmethod
    def _get_kit_quantity(cls, picking, bom):
        """Returns the quantity of kits in a transfer."""
        filters = {
            "incoming_moves": lambda m: True,
            "outgoing_moves": lambda m: False,
        }
        kit_quantity = picking.move_lines._compute_kit_quantities(
            bom.product_id, max(picking.move_lines.mapped("product_qty")), bom, filters
        )
        return kit_quantity

    def _check_move_lines(self, picking, move_lines):
        moves = []
        for move in picking.move_lines:
            moves.append((move.product_id, move.product_qty, bool(move.bom_line_id)))
        self.assertEqual(set(moves), set(move_lines))

    def test_split_picking_kit_no_split(self):
        """Check number of kits is equal to the split limit.

        No split is needed.
        """
        picking = self._create_picking(
            [
                (self.product_garden_table, 3),
            ]
        )
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=picking.ids)
            .create({"mode": "kit_quantity", "kit_split_quantity": 3})
        )
        res = wizard.action_apply()
        new_picking = self._get_picking_ids_from_action(res, 0)
        self.assertFalse(new_picking)
        np_kq = self._get_kit_quantity(picking, self.bom_garden_table)
        self.assertEqual(np_kq, 3)

    def test_split_picking_kit_single_split(self):
        """Check number of kits is 4 and the split limit is 3.

        New picking is created and one kit is moved to it.

        """
        picking = self._create_picking(
            [
                (self.product_garden_table, 4),
            ]
        )
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=picking.ids)
            .create({"mode": "kit_quantity", "kit_split_quantity": 3})
        )
        res = wizard.action_apply()
        # There is 3 kits left
        np_kq = self._get_kit_quantity(picking, self.bom_garden_table)
        self.assertEqual(np_kq, 3)
        # And one kit in the new picking
        new_picking = self._get_picking_ids_from_action(res, 1)
        np_kq = self._get_kit_quantity(new_picking, self.bom_garden_table)
        self.assertEqual(np_kq, 1)

    def test_split_picking_kit_with_no_kit(self):
        """Check split picking only has non kit product."""
        picking = self._create_picking(
            [(self.product_garden_table_top, 3), (self.product_garden_table_leg, 21)]
        )
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=picking.ids)
            .create({"mode": "kit_quantity", "kit_split_quantity": 7})
        )
        res = wizard.action_apply()
        expected_lines = [
            (self.product_garden_table_top, 3, False),
            (self.product_garden_table_leg, 4, False),
        ]
        self._check_move_lines(picking, expected_lines)
        new_picking = self._get_picking_ids_from_action(res, 1)
        expected_lines = [
            (self.product_garden_table_leg, 17, False),
        ]
        self._check_move_lines(new_picking, expected_lines)

    def test_split_picking_with_product_and_kit(self):
        picking = self._create_picking(
            [
                (self.product_garden_table_top, 3),
                (self.product_garden_table_leg, 21),
                (self.product_garden_table, 4),
            ]
        )
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=picking.ids)
            .create({"mode": "kit_quantity", "kit_split_quantity": 6})
        )
        res = wizard.action_apply()
        expected_lines = [
            (self.product_garden_table_top, 3, False),
            (self.product_garden_table_leg, 3, False),
        ]
        self._check_move_lines(picking, expected_lines)
        new_picking = self._get_picking_ids_from_action(res, 1)
        expected_lines = [
            (self.product_garden_table_leg, 18, False),
            (self.product_garden_table_top, 4, True),
            (self.product_garden_table_leg, 16, True),
        ]
        self._check_move_lines(new_picking, expected_lines)
