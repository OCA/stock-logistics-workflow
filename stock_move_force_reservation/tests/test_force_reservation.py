# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestForceReservation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env.ref("stock.warehouse0")
        self.product = self.env["product.product"].create(
            {
                "name": "TEST PRODUCT",
                "type": "product",
            }
        )
        self.partner_id = self.env.ref("base.res_partner_2")
        self.picking_type_id = self.env.ref("stock.picking_type_out")
        self.location_id = self.env.ref("stock.stock_location_stock")
        self.location_dest_id = self.env.ref("stock.stock_location_customers")
        self.product_uom = self.env.ref("uom.product_uom_unit")

    def test_force_availability(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 1,
            }
        )
        picking_id = self.env["stock.picking"].create(
            {
                "name": "Pick1",
                "partner_id": self.partner_id.id,
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "move1",
                            "product_id": self.product.id,
                            "product_uom": self.product_uom.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking_id.action_confirm()
        picking_id.action_assign()
        picking_id2 = self.env["stock.picking"].create(
            {
                "name": "Pick2",
                "partner_id": self.partner_id.id,
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "move2",
                            "product_id": self.product.id,
                            "product_uom": self.product_uom.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking_id2.action_confirm()
        picking_id.move_ids_without_package._compute_qty_in_stock()
        stock_move_id = picking_id.move_ids_without_package
        self.assertEqual(stock_move_id.qty_in_stock, 1)
        self.assertEqual(picking_id.state, "assigned")
        self.assertEqual(picking_id2.state, "confirmed")

        force_reservation_id = self.env["stock.move.force.reservation"].create(
            {
                "picking_id": picking_id2.id,
                "move_id": picking_id2.move_ids_without_package.id,
                "product_id": picking_id2.product_id.id,
                "move_to_unreserve_ids": [
                    (6, 0, [picking_id.move_ids_without_package.id])
                ],
            }
        )
        force_reservation_id._compute_total_quantity()
        self.assertEqual(force_reservation_id.total_quantity, 1)
        force_reservation_id.validate()
        self.assertEqual(picking_id.state, "confirmed")
        self.assertEqual(picking_id2.state, "assigned")
