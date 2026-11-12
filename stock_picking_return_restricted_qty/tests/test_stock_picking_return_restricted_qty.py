# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Command

from odoo.addons.base.tests.common import BaseCommon


class StockPickingReturnRestrictedQtyTest(BaseCommon):
    _test_user_groups = ("stock.group_stock_user",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "is_storable": True, "type": "consu"}
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, stock_location, 20
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 20,
                            "uom_id": cls.product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        }
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.move_ids.quantity = 20
        cls.picking.button_validate()

    def _set_restriction(self, restrict):
        self.picking_type_out.sudo().restrict_return_qty = restrict

    def _validate(self, picking):
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = picking.move_ids.product_uom_qty
        picking.move_ids.picked = True
        picking._action_done()

    def test_return_not_allowed(self):
        """A return demand above the delivered quantity is refused"""
        self._set_restriction(True)
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 0)
        with self.assertRaises(UserError):
            return_picking.move_ids.product_uom_qty = 30
        return_picking.move_ids.product_uom_qty = 20
        self.assertEqual(return_picking.move_ids.product_uom_qty, 20)

    def test_return_without_restriction(self):
        """Without the restriction the core behavior is kept"""
        self._set_restriction(False)
        return_picking = self.picking._create_return()
        return_picking.move_ids.product_uom_qty = 30
        self._validate(return_picking)
        self.assertEqual(return_picking.state, "done")
        self.assertEqual(return_picking.move_ids.quantity, 30)

    def test_multiple_return(self):
        """Each return only allows what is still on the customer hands"""
        self._set_restriction(True)
        first_return = self.picking._create_return()
        first_return.move_ids.product_uom_qty = 10
        self._validate(first_return)
        second_return = self.picking._create_return()
        with self.assertRaises(UserError):
            second_return.move_ids.product_uom_qty = 11
        second_return.move_ids.product_uom_qty = 10
        self._validate(second_return)
        self.assertEqual(second_return.state, "done")
        third_return = self.picking._create_return()
        with self.assertRaises(UserError):
            third_return.move_ids.product_uom_qty = 1

    def test_multiple_return_without_restriction(self):
        """Without the restriction a second return can exceed the rest"""
        self._set_restriction(False)
        first_return = self.picking._create_return()
        first_return.move_ids.product_uom_qty = 10
        self._validate(first_return)
        second_return = self.picking._create_return()
        second_return.move_ids.product_uom_qty = 80
        self.assertEqual(second_return.move_ids.product_uom_qty, 80)

    def test_return_all_restricted(self):
        """Return all is capped to the quantity still on the customer hands"""
        self._set_restriction(True)
        delivered_move = self.picking.move_ids
        chained_move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 8,
                "uom_id": self.product.uom_id.id,
                "location_id": delivered_move.location_dest_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "move_orig_ids": [Command.link(delivered_move.id)],
            }
        )
        chained_move._action_confirm()
        chained_move._action_assign()
        chained_move.quantity = 8
        chained_move.picked = True
        chained_move._action_done()
        self.assertEqual(chained_move.state, "done")
        return_picking = self.picking._create_return()
        return_picking.action_return_all()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 12)

    def test_return_of_return(self):
        """A return of a return also counts the previous returns of it"""
        self._set_restriction(True)
        self.picking_type_out.return_picking_type_id.sudo().restrict_return_qty = True
        first_return = self.picking._create_return()
        first_return.move_ids.product_uom_qty = 10
        self._validate(first_return)
        redelivery = first_return._create_return()
        redelivery.move_ids.product_uom_qty = 10
        self._validate(redelivery)
        second_redelivery = first_return._create_return()
        with self.assertRaises(UserError):
            second_redelivery.move_ids.product_uom_qty = 1

    def _deliver_two_dozens(self):
        dozen = self.env.ref("uom.product_uom_dozen")
        self.env["stock.quant"].sudo()._update_available_quantity(
            self.product, self.env.ref("stock.stock_location_stock"), 24
        )
        picking = self.picking.copy()
        picking.move_ids.write({"product_uom_qty": 2, "uom_id": dozen.id})
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = 2
        picking.button_validate()
        return picking

    def test_return_restricted_other_uom(self):
        """Returns in another UoM are counted in the product UoM"""
        self._set_restriction(True)
        picking = self._deliver_two_dozens()
        first_return = picking._create_return()
        first_return.move_ids.product_uom_qty = 1
        self._validate(first_return)
        second_return = picking._create_return()
        with self.assertRaises(UserError):
            second_return.move_ids.product_uom_qty = 1.5
        second_return.move_ids.product_uom_qty = 1
        self.assertEqual(second_return.move_ids.product_qty, 12)

    def test_return_all_restricted_other_uom(self):
        """Return all in another UoM is capped without raising"""
        self._set_restriction(True)
        stock_location = self.env.ref("stock.stock_location_stock")
        picking = self._deliver_two_dozens()
        delivered_move = picking.move_ids
        chained_move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "uom_id": self.product.uom_id.id,
                "location_id": delivered_move.location_dest_id.id,
                "location_dest_id": stock_location.id,
                "move_orig_ids": [Command.link(delivered_move.id)],
            }
        )
        chained_move._action_confirm()
        chained_move.quantity = 1
        chained_move.picked = True
        chained_move._action_done()
        return_picking = picking._create_return()
        return_picking.action_return_all()
        # 23 units left, rounded down to the dozen precision
        self.assertEqual(return_picking.move_ids.product_uom_qty, 1.91)

    def test_validate_ignores_unpicked_lines(self):
        """Lines that are not picked are dropped and do not count"""
        self._set_restriction(True)
        return_picking = self.picking._create_return()
        return_picking.move_ids.product_uom_qty = 20
        return_picking.action_confirm()
        return_picking.action_assign()
        move = return_picking.move_ids
        move.move_line_ids.write({"quantity": 20, "picked": True})
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": self.product.id,
                "quantity": 5,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "picked": False,
            }
        )
        return_picking._action_done()
        self.assertEqual(return_picking.state, "done")
        self.assertEqual(move.quantity, 20)

    def test_validate_more_than_delivered(self):
        """The done quantity of a return is also checked when validating"""
        self._set_restriction(True)
        return_picking = self.picking._create_return()
        return_picking.move_ids.product_uom_qty = 20
        return_picking.action_confirm()
        return_picking.action_assign()
        return_picking.move_ids.quantity = 25
        return_picking.move_ids.picked = True
        with self.assertRaises(UserError):
            return_picking._action_done()
