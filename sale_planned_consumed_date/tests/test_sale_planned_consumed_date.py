# Copyright 2024-2025 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import TransactionCase


class SaleOrderPlannedConsumedDateTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "test_product1", "type": "product"}
        )
        cls.order = cls.env["sale.order"].create(
            [
                {
                    "partner_id": cls.partner.id,
                    "commitment_date": "2024-02-02",
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": cls.product1.name,
                                "product_id": cls.product1.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.product1.uom_id.id,
                            },
                        ),
                    ],
                },
            ]
        )

    def test_confirm_sale_order_propagate_commitment_date_as_planned_consumed_date(
        self,
    ):
        self.order.action_confirm()
        delivery = self.order.picking_ids
        self.assertEqual(
            delivery.move_ids.planned_consumed_date,
            fields.Datetime.from_string("2024-02-02"),
        )

    def test_confirm_sale_order_without_commitment_date(
        self,
    ):
        self.order.commitment_date = False
        self.order.action_confirm()
        delivery = self.order.picking_ids
        self.assertFalse(
            delivery.move_ids.planned_consumed_date,
        )
