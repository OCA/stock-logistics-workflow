# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form


class TestGroupByBase:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.carrier1 = cls.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.carrier2 = cls.env["delivery.carrier"].create(
            {
                "name": "My Other Test Carrier",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.env.ref("stock.warehouse0").group_shippings = True
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def _update_qty_in_location(self, location, product, quantity):
        quants = self.env["stock.quant"]._gather(product, location, strict=True)
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        if quantity <= 0:
            quants.unlink()
        else:
            self.env["stock.quant"]._update_available_quantity(
                product, location, quantity
            )

    def _set_line(self, sale_form, amount=10.0):
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = amount
        # return line_form.save()

    def _get_new_sale_order(self, amount=10.0, partner=None, carrier=None):
        """Creates and returns a sale order with one default order line.

        :param float amount: quantity of product for the order line (10 by default)
        """
        if partner is None:
            partner = self.partner
        if carrier is None:
            carrier_id = False
        else:
            carrier_id = carrier
        with Form(self.env["sale.order"]) as sale_form:
            sale_form.partner_id = partner
            self._set_line(sale_form, amount)
        sale = sale_form.save()
        if carrier:
            wiz_action = sale.action_open_delivery_wizard()
            choose_delivery_carrier = (
                self.env[wiz_action["res_model"]]
                .with_context(**wiz_action["context"])
                .create({"carrier_id": carrier_id.id, "order_id": sale.id})
            )
            choose_delivery_carrier.button_confirm()
            sale.invalidate_recordset(fnames=["carrier_id"])
        return sale

    def _validate_transfer(self, picking):
        for move_line in picking.move_ids:
            move_line.picked = True
        picking._action_done()
