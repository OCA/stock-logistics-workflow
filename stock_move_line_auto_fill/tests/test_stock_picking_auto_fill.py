# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import Form, common


@common.tagged("-at_install", "post_install")
class TestStockPicking(common.TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()

        # models
        self.picking_model = self.env["stock.picking"]
        self.move_model = self.env["stock.move"]

        # warehouse and picking types
        self.warehouse = self.env.ref("stock.stock_warehouse_shop0")
        self.picking_type_in = self.env.ref("stock.chi_picking_type_in")
        self.picking_type_out = self.env.ref("stock.chi_picking_type_out")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")

        # Allow all companies for OdooBot user and set default user company
        # to warehouse company
        companies = self.env["res.company"].search([])
        self.env.user.company_ids = [(6, 0, companies.ids)]
        self.env.user.company_id = self.warehouse.company_id

        # products
        self.product_8 = self.env.ref("product.product_product_8")
        self.product_9 = self.env.ref("product.product_product_9")
        self.product_10 = self.env.ref("product.product_product_10")
        self.product_11 = self.env.ref("product.product_product_11")
        self.product_12 = self.env.ref("product.product_product_12")

        # supplier
        self.supplier = self.env.ref("base.res_partner_1")
        # customer
        self.customer = self.env.ref("base.res_partner_12")

        self.picking = self.picking_model.with_context(
            default_picking_type_id=self.picking_type_in.id
        ).create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
            }
        )
        self.picking_out = self.picking_model.with_context(
            default_picking_type_id=self.picking_type_out.id
        ).create(
            {
                "partner_id": self.customer.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.dozen = self.env.ref("uom.product_uom_dozen")

    def test_compute_action_pack_operation_auto_fill_allowed(self):

        self.move_model.create(
            dict(
                product_id=self.product_9.id,
                picking_id=self.picking.id,
                name=self.product_9.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_9.uom_id.id,
            )
        )

        # the auto fill action isn't available when picking is in draft
        # state.
        self.assertEqual(self.picking.state, "draft")
        self.assertFalse(self.picking.action_pack_op_auto_fill_allowed)

        # the auto fill action isn't available if no pack operation is
        # created.
        self.picking.state = "assigned"
        self.assertFalse(self.picking.action_pack_op_auto_fill_allowed)

        # The auto fill action is available when picking is assigned and
        # the picking have already pack operations.
        self.picking.action_confirm()
        self.assertTrue(self.picking.action_pack_op_auto_fill_allowed)

    def test_check_action_pack_operation_auto_fill_allowed(self):

        self.move_model.create(
            dict(
                product_id=self.product_9.id,
                picking_id=self.picking.id,
                name=self.product_9.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_9.uom_id.id,
            )
        )

        # the auto fill action isn't available when picking is in draft
        # state.
        self.assertEqual(self.picking.state, "draft")
        with self.cr.savepoint(), self.assertRaises(UserError):
            self.picking.action_pack_operation_auto_fill()

        # the auto fill action isn't available if no pack operation is
        # created.
        self.picking.state = "assigned"
        with self.cr.savepoint(), self.assertRaises(UserError):
            self.picking.action_pack_operation_auto_fill()

        # The auto fill action is available when picking is assigned and
        # the picking have already pack operations.
        self.picking.action_confirm()
        self.picking.action_pack_operation_auto_fill()

    def test_action_pack_operation_auto_fill(self):

        # set tracking on the products
        self.picking_type_in.use_create_lots = True
        self.product_8.tracking = "lot"
        self.product_9.tracking = "none"
        self.product_10.tracking = "serial"
        self.product_11.tracking = "none"

        self.move_model.create(
            dict(
                product_id=self.product_8.id,
                picking_id=self.picking.id,
                name=self.product_8.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_8.uom_id.id,
            )
        )

        self.move_model.create(
            dict(
                product_id=self.product_9.id,
                picking_id=self.picking.id,
                name=self.product_9.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_9.uom_id.id,
            )
        )

        self.move_model.create(
            dict(
                product_id=self.product_10.id,
                picking_id=self.picking.id,
                name=self.product_10.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_10.uom_id.id,
            )
        )

        self.move_model.create(
            dict(
                product_id=self.product_11.id,
                picking_id=self.picking.id,
                name=self.product_11.display_name + " pack",
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_11.uom_id.id,
            )
        )

        self.move_model.create(
            dict(
                product_id=self.product_12.id,
                picking_id=self.picking.id,
                name=self.product_12.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.dozen.id,
            )
        )

        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(len(self.picking.move_line_ids), 5)

        # At this point for each move we have an operation created.
        product_8_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_8
        )
        self.assertTrue(product_8_op)

        product_9_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_9
        )
        self.assertTrue(product_9_op)

        product_11_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_11
        )
        self.assertTrue(product_11_op)

        product_12_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_12
        )

        # replace the product_id with a pack in for the product_11_op
        # operation
        pack = self.env["stock.quant.package"].create(
            {
                "quant_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_11.id,
                            "quantity": 1,
                            "location_id": self.supplier_location.id,
                            "product_uom_id": self.product_11.uom_id.id,
                        },
                    )
                ]
            }
        )

        product_11_op.write({"package_id": pack.id})

        product_10_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_10
        )
        self.assertTrue(product_10_op)

        # Try to fill all the operation automatically.
        # The expected result is only operations with product_id set and
        # the product_id.tracking == none, have a qty_done set.
        self.picking.action_pack_operation_auto_fill()
        self.assertFalse(product_8_op.qty_done)
        self.assertEqual(product_9_op.product_uom_qty, product_9_op.qty_done)
        self.assertFalse(product_10_op.qty_done)
        self.assertEqual(product_11_op.product_uom_qty, product_11_op.qty_done)
        self.assertEqual(product_12_op.product_uom_qty, product_12_op.qty_done)

    def test_action_auto_transfer(self):
        # set tracking on the products
        self.picking_type_in.auto_fill_operation = True
        self.product_8.tracking = "lot"
        self.product_9.tracking = "none"

        self.move_model.create(
            dict(
                product_id=self.product_8.id,
                picking_id=self.picking.id,
                name=self.product_8.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_8.uom_id.id,
            )
        )

        self.move_model.create(
            dict(
                product_id=self.product_9.id,
                picking_id=self.picking.id,
                name=self.product_9.display_name,
                picking_type_id=self.picking_type_in.id,
                product_uom_qty=1.0,
                location_id=self.supplier_location.id,
                location_dest_id=self.picking_type_in.default_location_dest_id.id,
                product_uom=self.product_9.uom_id.id,
            )
        )

        self.picking.action_assign()

        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(len(self.picking.move_line_ids), 2)

        # At this point for each move we have an operation created.
        product_8_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_8
        )
        self.assertTrue(product_8_op)

        product_9_op = self.picking.move_line_ids.filtered(
            lambda p: p.product_id == self.product_9
        )
        self.assertTrue(product_9_op)

        # Try to fill all the operation automatically.
        # The expected result is only opertions with product_id set and
        self.assertTrue(product_8_op.qty_done)
        self.assertTrue(product_9_op.qty_done)

    def test_action_auto_transfer_avoid_assign_lots(self):
        # set tracking on the products
        self.picking_type_out.auto_fill_operation = True
        self.picking_type_out.avoid_lot_assignment = True
        self.product_8.tracking = "lot"
        self.product_9.tracking = "none"
        self.lot8 = self.env["stock.production.lot"].create(
            {
                "company_id": self.warehouse.company_id.id,
                "product_id": self.product_8.id,
                "name": "Lot 1",
            }
        )
        self.quant8 = self.env["stock.quant"].create(
            {
                "product_id": self.product_8.id,
                "location_id": self.picking_out.location_id.id,
                "quantity": 6,
                "lot_id": self.lot8.id,
            }
        )
        self.quant9 = self.env["stock.quant"].create(
            {
                "product_id": self.product_9.id,
                "location_id": self.picking_out.location_id.id,
                "quantity": 10,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_8.id,
                "picking_id": self.picking_out.id,
                "name": self.product_8.display_name,
                "picking_type_id": self.picking_type_out.id,
                "product_uom_qty": 1.0,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product_8.uom_id.id,
            }
        )

        self.move_model.create(
            {
                "product_id": self.product_9.id,
                "picking_id": self.picking_out.id,
                "name": self.product_9.display_name,
                "picking_type_id": self.picking_type_out.id,
                "product_uom_qty": 10.0,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product_9.uom_id.id,
            }
        )

        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.state, "assigned")
        self.assertEqual(len(self.picking_out.move_line_ids), 2)
        # At this point for each move we have an operation created.
        product_8_op = self.picking_out.move_line_ids.filtered(
            lambda p: p.product_id == self.product_8
        )
        self.assertTrue(product_8_op)
        product_9_op = self.picking_out.move_line_ids.filtered(
            lambda p: p.product_id == self.product_9
        )
        self.assertTrue(product_9_op)

        # Try to fill all the operation automatically.
        # The expected result is only opertions with product_id set and
        self.assertFalse(product_8_op.qty_done)
        self.assertTrue(product_9_op.qty_done)

    def test_action_assign_replenish_stock(self):
        # Covered case:
        # For a product with less stock than initial demand, check after
        # replenish stock that quantity done is written with initial demand
        # after check availability
        self.picking_type_in.auto_fill_operation = True
        product = self.env["product.product"].create(
            {"name": "Test auto fill", "type": "product"}
        )
        product_quant = self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "quantity": 1000.00,
            }
        )
        self.move_model.create(
            dict(
                product_id=product.id,
                picking_id=self.picking.id,
                name=product.display_name,
                picking_type_id=self.picking_type_out.id,
                product_uom_qty=1500.00,
                location_id=self.picking_type_out.default_location_src_id.id,
                location_dest_id=self.customer_location.id,
                product_uom=product.uom_id.id,
            )
        )
        self.picking.action_assign()
        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(len(self.picking.move_line_ids), 1)
        # Try to fill all the operation automatically.
        self.assertEqual(self.picking.move_line_ids.qty_done, 1000.00)
        product_quant.quantity = 1500.00
        self.picking.action_assign()
        self.assertEqual(self.picking.move_line_ids.qty_done, 1500.00)

    def _picking_return(self, picking, qty):
        # Make a return from picking
        ReturnWiz = self.env["stock.return.picking"]
        return_form = Form(
            ReturnWiz.with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        stock_return_picking = return_form.save()
        stock_return_picking.product_return_moves.quantity = qty
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(
            stock_return_picking_action["res_id"]
        )
        return_pick.action_assign()
        # return_pick.move_lines.quantity_done = qty
        return_pick._action_done()
        return return_pick

    def test_return_twice(self):
        # Covered case:
        # Return more than one times not duplicate quant units in stock
        self.picking_type_out.auto_fill_operation = True
        self.picking_type_in.auto_fill_operation = True
        product = self.env["product.product"].create(
            {"name": "Test return", "type": "product"}
        )
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "quantity": 500.00,
            }
        )
        self.move_model.create(
            dict(
                product_id=product.id,
                picking_id=self.picking_out.id,
                name=product.display_name,
                picking_type_id=self.picking_type_out.id,
                product_uom_qty=500.00,
                location_id=self.picking_type_out.default_location_src_id.id,
                location_dest_id=self.customer_location.id,
                product_uom=product.uom_id.id,
            )
        )
        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        # self.picking_out.move_lines.quantity_done = 500
        self.picking_out._action_done()
        self.assertEqual(product.qty_available, 0.0)

        # Make first return from customer location to stock location
        returned_picking = self._picking_return(self.picking_out, 500.00)
        self.assertEqual(product.qty_available, 500)

        # Make second return from stock location to customer location
        returned_picking = self._picking_return(returned_picking, 500.00)
        self.assertEqual(product.qty_available, 0.0)

        # Make third return from customer location to stock location
        returned_picking = self._picking_return(returned_picking, 500.00)

        self.assertEqual(product.qty_available, 500)
