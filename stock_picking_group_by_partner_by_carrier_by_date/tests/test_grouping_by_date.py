# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo.tests import SavepointCase, tagged


class TestGroupByDateBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.out_type_id.group_pickings = True
        cls.warehouse.out_type_id.group_pickings_by_date = True

    def _create_order(self, partner=None):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
            }
        )
        return order


@tagged("post_install", "-at_install")
class TestGroupByDate(TestGroupByDateBase):
    def _create_orders_and_pickings(self):
        order1 = self._create_order(partner=self.partner)
        order1.action_confirm()
        picking1 = order1.picking_ids
        order2 = self._create_order(partner=self.partner)
        order2.action_confirm()
        picking2 = order2.picking_ids
        return picking1, picking2

    def test_group_by_date(self):
        # Schedule orders for tomorrow
        with freeze_time("2020-11-27 12:00:00"):
            p1, p2 = self._create_orders_and_pickings()
            self.assertEqual(p1, p2)

        # Same day, inside time window
        with freeze_time("2020-11-27 11:00:00"):
            p3, p4 = self._create_orders_and_pickings()
            self.assertEqual(p3, p4)
            self.assertEqual(p3, p1)

        # Same day, out of time window
        with freeze_time("2020-11-27 18:00:00"):
            p5, p6 = self._create_orders_and_pickings()
            self.assertEqual(p5, p6)
            self.assertNotEqual(p5, p1)

        # Delay 1st picking date
        p1.scheduled_date = "2020-11-27 18:30:00"
        with freeze_time("2020-11-27 18:00:00"):
            p5, p6 = self._create_orders_and_pickings()
            self.assertEqual(p5, p6)
            self.assertEqual(p5, p1)

        # Previous day
        with freeze_time("2020-11-26 08:00:00"):
            p7, p8 = self._create_orders_and_pickings()
            self.assertEqual(p7, p8)
            self.assertNotEqual(p7, p1)

        # Day after
        with freeze_time("2020-11-28 14:00:00"):
            p9, p10 = self._create_orders_and_pickings()
            self.assertEqual(p9, p10)
            self.assertNotEqual(p9, p1)
