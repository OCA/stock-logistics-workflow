# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestProcurementGroupCarrierCommon(TransactionCase):
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
        cls.carrier2 = cls.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier2",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.carrier3 = cls.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier3",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    @classmethod
    def _add_carrier_to_order(cls, order, carrier):
        wiz_action = order.action_open_delivery_wizard()
        choose_delivery_carrier = (
            cls.env[wiz_action["res_model"]]
            .with_context(**wiz_action["context"])
            .create({"carrier_id": carrier.id, "order_id": order.id})
        )
        choose_delivery_carrier.button_confirm()

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
