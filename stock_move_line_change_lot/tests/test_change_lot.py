# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import namedtuple

from odoo.tests import Form, TransactionCase


class ChangeLotCase(TransactionCase):
    """Tests covering changing a lot on a move line"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.wh = cls.env.ref("stock.warehouse0")
        cls.picking_type = cls.wh.out_type_id
        cls.picking_type.sudo().show_entire_packs = True
        cls.shelf1 = cls.env.ref("stock.stock_location_components")
        cls.shelf2 = cls.env.ref("stock.stock_location_14")

        cls.product_a = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product A",
                    "is_storable": True,
                    "tracking": "lot",
                }
            )
        )
        cls.product_b = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product B",
                    "is_storable": True,
                }
            )
        )

    # used by _create_package_in_location
    PackageContent = namedtuple(
        "PackageContent",
        # recordset of the product,
        # quantity in float
        # recordset of the lot (optional)
        "product quantity lot",
    )

    def _create_lot(self, product):
        return self.env["stock.lot"].create(
            {"product_id": product.id, "company_id": self.env.company.id}
        )

    def _create_package_in_location(self, location, content):
        """Create a package and quants in a location

        content is a list of PackageContent
        """
        package = self.env["stock.quant.package"].create({})
        for product, quantity, lot in content:
            self._update_qty_in_location(
                location, product, quantity, package=package, lot=lot
            )
        return package

    @classmethod
    def _create_picking(cls, picking_type=None, lines=None, confirm=True, **kw):
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = picking_type or cls.picking_type
        if lines is None:
            lines = [(cls.product_a, 10), (cls.product_b, 10)]
        for product, qty in lines:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.product_uom_qty = qty
        for k, v in kw.items():
            setattr(picking_form, k, v)
        picking = picking_form.save()
        if confirm:
            picking.action_confirm()
        return picking

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product, location, quantity, package_id=package, lot_id=lot
        )

    @classmethod
    def _change_lot(cls, line, lot):
        line.write(
            {
                "lot_id": lot.id,
                "package_id": False,
                "result_package_id": False,
            }
        )

    def assert_quant_reserved_qty(self, move_line, qty_func, package=None, lot=None):
        domain = [
            ("location_id", "=", move_line.location_id.id),
            ("product_id", "=", move_line.product_id.id),
        ]
        if package:
            domain.append(("package_id", "=", package.id))
        if lot:
            domain.append(("lot_id", "=", lot.id))
        quant = self.env["stock.quant"].search(domain)
        self.assertEqual(quant.reserved_quantity, qty_func())

    def assert_quant_package_qty(self, location, package, qty_func):
        quant = self.env["stock.quant"].search(
            [("location_id", "=", location.id), ("package_id", "=", package.id)]
        )
        self.assertEqual(quant.quantity, qty_func())

    def test_change_lot(self):
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        source_location = line.location_id
        new_lot = self._create_lot(self.product_a)
        # ensure we have our new package in the same location
        self._update_qty_in_location(source_location, line.product_id, 10, lot=new_lot)
        self._change_lot(line, new_lot)
        self.assertRecordValues(line, [{"lot_id": new_lot.id}])
        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, lot=new_lot
        )

    def test_change_lot_less_quantity(self):
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        source_location = line.location_id
        new_lot = self._create_lot(self.product_a)
        # ensure we have our new package in the same location
        self._update_qty_in_location(source_location, line.product_id, 8, lot=new_lot)
        self._change_lot(line, new_lot)
        self.assertRecordValues(
            line, [{"lot_id": new_lot.id, "quantity_product_uom": 8}]
        )
        other_line = line.move_id.move_line_ids - line
        self.assertRecordValues(
            other_line, [{"lot_id": initial_lot.id, "quantity_product_uom": 2}]
        )
        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 2, lot=initial_lot)
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, lot=new_lot
        )

    def test_change_lot_zero_quant(self):
        """No quant in the location for the scanned lot"""
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        new_lot = self._create_lot(self.product_a)
        self._change_lot(line, new_lot)
        self.assertRecordValues(
            line, [{"lot_id": new_lot.id, "quantity_product_uom": 0}]
        )
        # check that reservations have not been updated
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(line, lambda: 0, lot=new_lot)

    def test_change_lot_package_explode(self):
        """Scan a lot on units replacing a package"""
        initial_lot = self._create_lot(self.product_a)
        package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=initial_lot)]
        )
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self.assertEqual(line.lot_id, initial_lot)
        self.assertEqual(line.package_id, package)

        new_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=new_lot)
        self._change_lot(line, new_lot)

        self.assertRecordValues(
            line,
            [
                {
                    "lot_id": new_lot.id,
                    "quantity_product_uom": 10,
                    "package_id": False,
                    "package_level_id": False,
                }
            ],
        )

        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, lot=new_lot
        )

    def test_change_lot_reserved_qty(self):
        """Scan a lot already reserved by other lines

        It should unreserve the other line, use the lot for the current line,
        and re-reserve the other move.
        """
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self.assertEqual(line.lot_id, initial_lot)

        new_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=new_lot)
        picking2 = self._create_picking(lines=[(self.product_a, 10)])
        picking2.action_assign()
        line2 = picking2.move_line_ids
        self.assertEqual(line2.lot_id, new_lot)

        self._change_lot(line, new_lot)
        self.assertRecordValues(
            line, [{"lot_id": new_lot.id, "quantity_product_uom": 10}]
        )
        # line has been re-created
        line2 = picking2.move_line_ids
        self.assertRecordValues(
            line2, [{"lot_id": initial_lot.id, "quantity_product_uom": 10}]
        )

        # check that reservations have been updated
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, lot=new_lot
        )
        self.assert_quant_reserved_qty(
            line2, lambda: line2.quantity_product_uom, lot=initial_lot
        )

    def test_change_lot_reserved_partial_qty(self):
        """Scan a lot already reserved by other lines and can only be reserved
        partially

        It should unreserve the other line, use the lot for the current line,
        and re-reserve the other move. The quantity for the current line must
        be adapted to the available
        """
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self.assertEqual(line.lot_id, initial_lot)

        new_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 8, lot=new_lot)
        picking2 = self._create_picking(lines=[(self.product_a, 8)])
        picking2.action_assign()
        line2 = picking2.move_line_ids
        self.assertEqual(line2.lot_id, new_lot)

        self._change_lot(line, new_lot)

        self.assertRecordValues(
            line, [{"lot_id": new_lot.id, "quantity_product_uom": 8}]
        )
        other_line = picking.move_line_ids - line
        self.assertRecordValues(
            other_line, [{"lot_id": initial_lot.id, "quantity_product_uom": 2}]
        )
        # line has been re-created
        line2 = picking2.move_line_ids
        self.assertRecordValues(
            line2, [{"lot_id": initial_lot.id, "quantity_product_uom": 8}]
        )

        # check that reservations have been updated
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, lot=new_lot
        )
        # both line2 and the line for the 2 remaining will re-reserve the initial lot
        self.assert_quant_reserved_qty(
            other_line,
            lambda: line2.quantity_product_uom + other_line.quantity_product_uom,
            lot=initial_lot,
        )

    def test_change_lot_reserved_qty_done(self):
        """Scan a lot already reserved by other *picked* lines

        Cannot "steal" lot from picked lines
        """
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self.assertEqual(line.lot_id, initial_lot)

        new_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=new_lot)
        picking2 = self._create_picking(lines=[(self.product_a, 10)])
        picking2.action_assign()
        line2 = picking2.move_line_ids
        self.assertEqual(line2.lot_id, new_lot)
        line2.picked = True

        self._change_lot(line, new_lot)

        # no reservation
        self.assertRecordValues(
            line, [{"lot_id": new_lot.id, "quantity_product_uom": 0}]
        )
        self.assertRecordValues(
            line2, [{"lot_id": new_lot.id, "quantity_product_uom": 10, "picked": True}]
        )
        # A new line is created to reserve the quantity
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(
            line2, lambda: line2.quantity_product_uom, lot=new_lot
        )

    def test_change_lot_different_location(self):
        "If the scanned lot is in a different location, we cannot process it"
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        new_lot = self._create_lot(self.product_a)
        # ensure we have our new lot in a different location
        self._update_qty_in_location(self.shelf2, line.product_id, 10, lot=new_lot)
        self._change_lot(line, new_lot)
        self.assertRecordValues(line, [{"lot_id": new_lot.id}])
        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(line, lambda: 0, lot=new_lot)

    def test_change_lot_in_package(self):
        initial_lot = self._create_lot(self.product_a)
        initial_package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=initial_lot)]
        )
        # ensure we have our new package in the same location
        new_lot = self._create_lot(self.product_a)
        new_package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=new_lot)]
        )
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self._change_lot(line, new_lot)
        self.assertRecordValues(
            line,
            [
                {
                    "package_id": new_package.id,
                    "result_package_id": False,
                    "lot_id": new_lot.id,
                    "quantity_product_uom": 10.0,
                }
            ],
        )
        self.assertEqual(line.package_level_id.id, False)
        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 0, package=initial_package)
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, package=new_package
        )

    def test_change_lot_in_package_no_initial_package(self):
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        # ensure we have our new package in the same location
        new_lot = self._create_lot(self.product_a)
        new_package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=new_lot)]
        )
        picking = self._create_picking(lines=[(self.product_a, 10)])
        picking.action_assign()
        line = picking.move_line_ids
        self._change_lot(line, new_lot)
        self.assertRecordValues(
            line,
            [
                {
                    "package_id": new_package.id,
                    "result_package_id": False,
                    "lot_id": new_lot.id,
                    "quantity_product_uom": 10.0,
                }
            ],
        )
        self.assertEqual(line.package_level_id.id, False)
        # check that reservations have been updated
        self.assert_quant_reserved_qty(line, lambda: 0, lot=initial_lot)
        self.assert_quant_reserved_qty(
            line, lambda: line.quantity_product_uom, package=new_package
        )
