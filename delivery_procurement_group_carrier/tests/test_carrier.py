# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase, tagged
from odoo.tests.common import Form


@tagged("post_install", "-at_install")
class TestProcurementGroupCarrier(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {"type": "product", "name": "Test Product"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    @classmethod
    def _add_carrier_to_order(cls, order, carrier):
        order.set_delivery_line(carrier, 1)

    @classmethod
    def _create_sale_order(cls, product_qty, carrier=None):
        with Form(cls.env["sale.order"]) as order_form:
            order_form.partner_id = cls.partner
            for product, qty in product_qty:
                with order_form.order_line.new() as line:
                    line.product_id = product
                    line.product_uom_qty = qty

        order = order_form.save()
        if carrier:
            cls._add_carrier_to_order(order, carrier)
        return order

    def test_sale_procurement_group_carrier(self):
        """Check the SO procurement group contains the carrier on SO confirmation"""
        order = self._create_sale_order([(self.product, 1.0)], carrier=self.carrier)
        order.action_confirm()
        self.assertTrue(order.picking_ids)
        self.assertEqual(order.procurement_group_id.carrier_id, order.carrier_id)

    def test_sale_picking_group_carrier_aligned(self):
        # Create an order without carrier
        order = self._create_sale_order([(self.product, 1.0)])
        order.action_confirm()
        picking = order.picking_ids
        move_group = picking.move_lines.group_id
        self.assertFalse(order.carrier_id)
        self.assertFalse(picking.carrier_id)
        self.assertFalse(move_group.carrier_id)
        # Now change carrier on order (odoo allows it)
        self._add_carrier_to_order(order, self.carrier)
        # In odoo standard both picking and order references the new carrier
        move_group = picking.move_lines.group_id
        self.assertEqual(order.carrier_id, self.carrier)
        self.assertEqual(picking.carrier_id, self.carrier)
        self.assertEqual(move_group.carrier_id, self.carrier)
