# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestStockMoveLineSplit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Splittable",
                "type": "consu",
                "is_storable": True,
                "weight": 2.0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Splittable 2",
                "type": "consu",
                "is_storable": True,
                "weight": 1.0,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create(
            {
                "name": "Pallet",
                "max_weight": 10.0,
                "base_weight": 2.0,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.stock, 100)
        cls.env["stock.quant"]._update_available_quantity(cls.product2, cls.stock, 100)

    @classmethod
    def _create_picking(cls, specs):
        picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock.id,
                "location_dest_id": cls.customers.id,
                "picking_type_id": cls.picking_type_out.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "location_id": cls.stock.id,
                            "location_dest_id": cls.customers.id,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                        },
                    )
                    for product, qty in specs
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        return picking

    @classmethod
    def _create_reserved_picking(cls, product, qty):
        return cls._create_picking([(product, qty)])

    def _run_wizard(self, move_lines, **vals):
        wizard = self.env["stock.move.line.split"].create(
            {
                "move_line_ids": [(6, 0, move_lines.ids)],
                **vals,
            }
        )
        moves = move_lines.move_id
        wizard.action_apply()
        return moves.move_line_ids

    def _reserved_qty(self, product, location):
        quants = self.env["stock.quant"]._gather(product, location)
        return sum(quants.mapped("reserved_quantity"))

    def test_split_fixed_with_remainder(self):
        picking = self._create_reserved_picking(self.product, 23)
        ml = picking.move_line_ids
        self.assertEqual(len(ml), 1)
        reserved_before = self._reserved_qty(self.product, self.stock)
        lines = self._run_wizard(ml, strategy="fixed", fixed_qty=5)
        self.assertEqual(sorted(lines.mapped("quantity")), [3.0, 5.0, 5.0, 5.0, 5.0])
        self.assertEqual(self._reserved_qty(self.product, self.stock), reserved_before)

    def test_split_fixed_exact(self):
        picking = self._create_reserved_picking(self.product, 20)
        lines = self._run_wizard(picking.move_line_ids, strategy="fixed", fixed_qty=5)
        self.assertEqual(sorted(lines.mapped("quantity")), [5.0, 5.0, 5.0, 5.0])
        self.assertEqual(len(lines), 4)

    def test_no_split_when_size_ge_quantity(self):
        picking = self._create_reserved_picking(self.product, 5)
        lines = self._run_wizard(picking.move_line_ids, strategy="fixed", fixed_qty=10)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines.quantity, 5.0)

    def test_fixed_qty_not_respecting_uom_rounding(self):
        category = self.env["uom.category"].create({"name": "Whole Units"})
        uom = self.env["uom.uom"].create(
            {
                "name": "Piece",
                "category_id": category.id,
                "uom_type": "reference",
                "rounding": 1.0,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Whole only",
                "type": "consu",
                "is_storable": True,
                "uom_id": uom.id,
                "uom_po_id": uom.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(product, self.stock, 10)
        picking = self._create_reserved_picking(product, 10)
        with self.assertRaises(UserError):
            self._run_wizard(picking.move_line_ids, strategy="fixed", fixed_qty=2.5)

    def test_split_weight_custom(self):
        # weight 2 / unit, custom max 5 -> = 2 units per line
        picking = self._create_reserved_picking(self.product, 7)
        reserved_before = self._reserved_qty(self.product, self.stock)
        lines = self._run_wizard(
            picking.move_line_ids,
            strategy="weight",
            weight_source="custom",
            max_weight=5,
        )
        self.assertEqual(sorted(lines.mapped("quantity")), [1.0, 2.0, 2.0, 2.0])
        self.assertEqual(self._reserved_qty(self.product, self.stock), reserved_before)

    def test_split_weight_package_type(self):
        # Pack type: max 10 - base 2 = 8 available, weight 2 / unit -> 4 per line
        picking = self._create_reserved_picking(self.product, 10)
        lines = self._run_wizard(
            picking.move_line_ids,
            strategy="weight",
            weight_source="package_type",
            package_type_id=self.package_type.id,
        )
        self.assertEqual(sorted(lines.mapped("quantity")), [2.0, 4.0, 4.0])

    def test_package_type_available_weight_compute(self):
        wizard = self.env["stock.move.line.split"].create(
            {
                "strategy": "weight",
                "weight_source": "package_type",
            }
        )
        wizard.package_type_id = self.package_type
        self.assertEqual(wizard.package_type_available_weight, 8.0)

    def test_single_unit_exceeds_max_weight(self):
        # weight 2 / unit, max 1 -> = 0 units -> cannot split
        picking = self._create_reserved_picking(self.product, 10)
        with self.assertRaises(UserError):
            self._run_wizard(
                picking.move_line_ids,
                strategy="weight",
                weight_source="custom",
                max_weight=1,
            )

    def test_package_type_non_positive_available_weight_raises(self):
        # max weight equals base weight -> 0 available
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Empty allowance",
                "max_weight": 2.0,
                "base_weight": 2.0,
            }
        )
        picking = self._create_reserved_picking(self.product, 10)
        with self.assertRaises(UserError):
            self._run_wizard(
                picking.move_line_ids,
                strategy="weight",
                weight_source="package_type",
                package_type_id=package_type.id,
            )

    def test_split_multiple_move_lines(self):
        picking = self._create_picking([(self.product, 23), (self.product2, 12)])
        move_lines = picking.move_line_ids
        self.assertEqual(len(move_lines), 2)
        lines = self._run_wizard(move_lines, strategy="fixed", fixed_qty=5)
        p_lines = lines.filtered(lambda line: line.product_id == self.product)
        p2_lines = lines.filtered(lambda line: line.product_id == self.product2)
        self.assertEqual(sorted(p_lines.mapped("quantity")), [3.0, 5.0, 5.0, 5.0, 5.0])
        self.assertEqual(sorted(p2_lines.mapped("quantity")), [2.0, 5.0, 5.0])
