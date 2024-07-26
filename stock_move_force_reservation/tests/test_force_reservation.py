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
        self.product2 = self.env["product.product"].create(
            {
                "name": "TEST PRODUCT2",
                "type": "product",
            }
        )
        self.partner_id = self.env.ref("base.res_partner_2")

    def test_force_availability(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 1,
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        so.picking_ids.action_assign()

        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        so2.action_confirm()
        so2.picking_ids.action_assign()
        self.assertEqual(so.picking_ids.state, "assigned")
        self.assertEqual(so2.picking_ids.state, "confirmed")

        self.env["stock.move.force.reservation"].create(
            {
                "picking_id": so2.picking_ids.id,
                "move_id": so2.picking_ids.move_ids_without_package.id,
                "product_id": so2.picking_ids.product_id.id,
                "move_to_unreserve_ids": [
                    (6, 0, so.picking_ids.move_ids_without_package.ids)
                ],
            }
        ).validate()
        self.assertEqual(so.picking_ids.state, "confirmed")
        self.assertEqual(so2.picking_ids.state, "assigned")
