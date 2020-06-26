# @author Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestQuickQuantityDone(TransactionCase):
    def setUp(self):
        super(TestQuickQuantityDone, self).setUp()
        partner = self.env['res.partner'].create({
            'name': 'Test',
        })
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        picking_type_out = self.env.ref("stock.picking_type_out")
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        # picking with initial demands
        self.picking = self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_1.name,
                            "product_id": self.product_id_1.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product_id_1.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_2.name,
                            "product_id": self.product_id_2.id,
                            "product_uom_qty": 7,
                            "product_uom": self.product_id_2.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
            }
        )
        self.picking.action_confirm()

        # picking2 with initial demands null
        self.picking2 = self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_1.name,
                            "product_id": self.product_id_1.id,
                            "product_uom_qty": 0,
                            "product_uom": self.product_id_1.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_2.name,
                            "product_id": self.product_id_2.id,
                            "product_uom_qty": 0,
                            "product_uom": self.product_id_2.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
            }
        )
        self.picking2.action_confirm()

        # picking2 with no line
        self.picking3 = self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
            }
        )
        self.picking3.action_confirm()


    def test_one_quantity_change(self):

        # test initial demands
        for line in self.picking.move_ids_without_package:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.quantity_done, 0)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.quantity_done, 0)

        # test with one manuel change
        for line in self.picking.move_ids_without_package:
            if line.product_id == self.product_id_1:
                line.quick_quantity_done()
                self.assertEqual(line.quantity_done, 5)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.quantity_done, 0)

    def test_all_quantities_done(self):

        # test with changing all quantities
        self.picking.quick_quantities_done()
        for line in self.picking.move_ids_without_package:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.quantity_done, 5)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.quantity_done, 7)

    def test_all_quantities_done_with_no_initial_demands(self):

        # test with changing all quantities
        with self.assertRaises(UserError):
            self.picking2.quick_quantities_done()


    def test_all_quantities_done_with_no_line(self):

        # test with changing all quantities
        with self.assertRaises(UserError):
            self.picking3.quick_quantities_done()
