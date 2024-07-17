# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form, common, tagged


@tagged("post_install", "-at_install")
class TestStockLockLot(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_stock_multi_locations = cls.env.ref("stock.group_stock_multi_locations")
        cls.env.user.write({"groups_id": [(4, group_stock_multi_locations.id, 0)]})
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "tracking": "serial",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.serial1 = cls.env["stock.production.lot"].create(
            {
                "name": "Serial1",
                "product_id": cls.product_serial.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.serial2 = cls.env["stock.production.lot"].create(
            {
                "name": "Serial2",
                "product_id": cls.product_serial.id,
                "company_id": cls.env.company.id,
            }
        )

    def create_picking(self, use_serial_product=True):
        product = self.product_serial if use_serial_product else self.product
        customer = self.env["res.partner"].create({"name": "SuperPartner"})
        picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Manual Lot Selection",
                "code": "outgoing",
                "sequence_code": "OUT",
                "use_create_lots": False,
                "use_existing_lots": False,
                "use_manual_lots": True,
                "default_location_src_id": self.stock_location.id,
                "default_location_dest_id": self.customer_location.id,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": customer.id,
                "picking_type_id": picking_type.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Move",
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": 1,
                "product_uom": product.uom_id.id,
            }
        )
        picking.action_confirm()
        return picking, move

    def add_picking_operation(
        self, picking, product, qty_done=0, lot=None, manual_lot=None
    ):
        with Form(picking) as picking_form:
            with picking_form.move_line_ids_without_package.new() as line_form:
                line_form.product_id = product
                line_form.qty_done = qty_done
                if lot:
                    line_form.lot_id = lot
                if manual_lot:
                    line_form.manual_production_lot_id = manual_lot
            picking_form.save()

    def test_01_no_manual_selection_with_done_qty(self):
        """No Manual selection of a serial with done qty should raise an error."""
        picking, move = self.create_picking()
        self.add_picking_operation(
            picking, move.product_id, qty_done=1, lot=self.serial1
        )
        with self.assertRaises(UserError):
            picking._action_done()

    def test_02_no_manual_selection_without_done_qty(self):
        """No Manual selection of a serial with done qty should raise an error."""
        picking, move = self.create_picking()
        self.add_picking_operation(
            picking, move.product_id, qty_done=0, lot=self.serial1
        )
        with self.assertRaises(UserError):
            picking._action_done()

    def test_03_manual_selection_without_done_qty(self):
        """No Manual selection of a serial without done qty should not raise an error."""
        picking, move = self.create_picking()
        self.add_picking_operation(
            picking,
            move.product_id,
            qty_done=0,
            lot=self.serial1,
            manual_lot=self.serial2,
        )
        picking._action_done()

    def test_04_manual_selection_with_done_qty(self):
        """Manual selection of a serial with done qty should not raise an error."""
        picking, move = self.create_picking()
        self.add_picking_operation(
            picking,
            move.product_id,
            qty_done=1,
            lot=self.serial1,
            manual_lot=self.serial2,
        )
        picking._action_done()

    def test_05_no_manual_selection_with_done_qty_raises_exception(self):
        """No Manual selection with done qty should raise an error."""
        picking, move = self.create_picking()
        self.add_picking_operation(
            picking, move.product_id, qty_done=1, lot=self.serial1
        )
        with self.assertRaises(UserError):
            picking._action_done()

    def test_06_untracked_product_with_done_qty(self):
        """Untracked product with done qty should not raise an error."""
        picking, move = self.create_picking(use_serial_product=False)
        self.add_picking_operation(picking, move.product_id, qty_done=1)
        picking._action_done()
