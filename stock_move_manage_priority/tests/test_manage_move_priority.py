# Copyright 2023 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import TransactionCase


class TestManageMovePriority(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.location_model = cls.env["stock.location"]
        cls.stock_location = cls.location_model.create({"name": "stock_loc"})
        cls.customer_location = cls.location_model.create({"name": "customer_loc"})
        cls.picking_type_out = cls.env.ref("stock.picking_type_out").id
        cls.picking_type_in = cls.env.ref("stock.picking_type_in").id
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product test",
                "uom_id": cls.uom_unit.id,
                "type": "product",
            }
        )
        cls.company = cls.env.user.company_id
        cls.company.stock_move_manage_priority = False

    def create_picking(self, picking_type, product, from_loc, to_loc):
        picking = self.picking_model.create(
            {
                "picking_type_id": picking_type,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
            }
        )
        self.move_model.create(
            {
                "name": self.product.name,
                "date": fields.Datetime.now(),
                "reservation_date": fields.Date.today(),
                "product_id": product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
            }
        )
        picking.action_confirm()
        return picking

    def test_move_priority(self):
        """
        - Create and confirm a picking with one move then you can't change the move's
          priority
        - Enable the move priority management but still can't change the move's
          priority
        - Unlock the picking then you can change the move's priority
        - Validate the move and you can't change the priority again
        """
        pick = self.create_picking(
            self.picking_type_out,
            self.product,
            self.stock_location,
            self.customer_location,
        )
        self.assertEqual(pick.priority, "0")
        self.assertEqual(pick.move_ids.priority, "0")
        self.assertFalse(pick.move_ids.is_priority_editable)  # priority not editable
        # try to change the priority on move
        pick.move_ids.priority = "1"
        # but it didn't work
        self.assertNotEqual(pick.move_ids.priority, "1")
        # enable move priority management
        self.assertFalse(self.company.stock_move_manage_priority)
        self.env["res.config.settings"].create(
            {"stock_move_manage_priority": True}
        ).execute()
        self.assertTrue(self.company.stock_move_manage_priority)
        self.assertFalse(pick.move_ids.is_priority_editable)  # priority not editable
        # try to change the priority on move
        pick.move_ids.priority = "1"
        # but it didn't work because the pick is locked
        self.assertNotEqual(pick.move_ids.priority, "1")
        self.assertTrue(pick.is_locked)
        # unlock the pick
        pick.action_toggle_is_locked()
        self.assertTrue(pick.move_ids.is_priority_editable)  # priority editable
        # try to change the priority on move
        pick.move_ids.priority = "1"
        # and it worked
        self.assertEqual(pick.move_ids.priority, "1")
        # set back the priority to normal
        pick.move_ids.priority = "0"
        self.assertEqual(pick.move_ids.priority, "0")
        # validate the move
        pick.move_ids.quantity_done = 1
        pick.button_validate()
        self.assertEqual(pick.state, "done")
        self.assertFalse(pick.move_ids.is_priority_editable)  # priority not editable
        # try to change the priority on move again
        pick.move_ids.priority = "1"
        # but it didn't work because the state is done
        self.assertNotEqual(pick.move_ids.priority, "1")
