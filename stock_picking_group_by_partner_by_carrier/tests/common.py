# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from odoo.addons.sale.tests.test_sale_common import TestSale


@tagged("post_install", "-at_install")
class TestGroupByBase(TestSale):
    # FIXME: TestSale is very heavy and create tons of records w/ no tracking disable
    # for every test. Move to SavepointCase!
    def setUp(self):
        super().setUp()
        self.carrier1 = self.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier",
                "product_id": self.env.ref("delivery.product_product_delivery").id,
            }
        )
        self.carrier2 = self.env["delivery.carrier"].create(
            {
                "name": "My Other Test Carrier",
                "product_id": self.env.ref("delivery.product_product_delivery").id,
            }
        )
        self.env.ref("stock.warehouse0").group_shippings = True
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def _update_qty_in_location(self, location, product, quantity):
        quants = self.env["stock.quant"]._gather(product, location, strict=True)
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def _get_new_sale_order(self, amount=10.0, partner=None, carrier=None):
        """Creates and returns a sale order with one default order line.

        :param float amount: quantity of product for the order line (10 by default)
        """
        if partner is None:
            partner = self.partner
        if carrier is None:
            carrier_id = False
        else:
            carrier_id = carrier.id
        product = self.env.ref("product.product_delivery_01")
        sale_order_vals = {
            "partner_id": partner.id,
            "partner_invoice_id": partner.id,
            "partner_shipping_id": partner.id,
            "carrier_id": carrier_id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": amount,
                        "product_uom": product.uom_id.id,
                        "price_unit": product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        sale_order = self.env["sale.order"].create(sale_order_vals)
        return sale_order
