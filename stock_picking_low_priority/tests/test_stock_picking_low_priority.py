# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import TransactionCase


class TestStockPickingLowPriority(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.location_model = cls.env["stock.location"]
        cls.stock_location = cls.location_model.create({"name": "stock_loc"})
        cls.supplier_location = cls.location_model.create({"name": "supplier_loc"})
        cls.customer_location = cls.location_model.create({"name": "custmer_loc"})
        cls.picking_type_out = cls.env.ref("stock.picking_type_out").id
        cls.picking_type_in = cls.env.ref("stock.picking_type_in").id
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "uom_id": cls.uom_unit.id,
                "type": "product",
            }
        )

    def create_picking(self, picking_type, from_loc, to_loc, sequence=10, delay=0):
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
                "sequence": sequence,
                "date": fields.Datetime.add(fields.Datetime.now(), second=delay),
                "reservation_date": fields.Date.today(),
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
            }
        )
        picking.action_confirm()
        return picking

    def test_selection_insertion(self):
        """
        Test that the 'Not urgent' priority has been inserted in first position of the
        selection
        """
        priority_selection = self.picking_model.fields_get()["priority"]["selection"]
        self.assertEqual(priority_selection[0], ("-1", "Not urgent"))

    def test_assign_qty_to_first_move(self):
        """
        Suppose two out picking waiting for an available quantity. When receiving such
        a quantity, the latter should be assign to the picking with the
        highest priority.
        """

        out01 = self.create_picking(
            self.picking_type_out, self.stock_location, self.customer_location
        )
        out02 = self.create_picking(
            self.picking_type_out,
            self.stock_location,
            self.customer_location,
            sequence=2,
            delay=1,
        )
        in01 = self.create_picking(
            self.picking_type_in, self.supplier_location, self.stock_location, delay=2
        )
        # normal priority for both out01 and out02 so out01 will be assigned before out02
        in01.move_ids.quantity_done = 1
        in01.button_validate()
        self.assertEqual(out01.state, "assigned")
        self.assertEqual(out02.state, "confirmed")

        out01.move_ids.quantity_done = 1
        out01.button_validate()

        out03 = self.create_picking(
            self.picking_type_out, self.stock_location, self.customer_location, delay=3
        )
        # set out02 to not urgent so out03 will be assigned before out02
        out02.priority = "-1"
        in02 = self.create_picking(
            self.picking_type_in, self.supplier_location, self.stock_location, delay=4
        )

        in02.move_ids.quantity_done = 1
        in02.button_validate()
        self.assertEqual(out03.state, "assigned")
        self.assertEqual(out02.state, "confirmed")
