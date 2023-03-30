# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestGroupMaxWeight(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.product_2 = cls.env.ref("product.product_delivery_02")
        cls.product_3 = cls.product_2.copy()
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.group_pickings_maxweight = 8.0

    def _set_line(self, sale_form, product, amount=10.0):
        with sale_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = amount

    def _get_new_sale_order(self, amount=10.0, partner=None):
        """Creates and returns a sale order with one default order line.
        :param float amount: quantity of product for the order line (10 by default)
        """
        if partner is None:
            partner = self.partner
        with Form(self.env["sale.order"]) as sale_form:
            sale_form.partner_id = partner
            self._set_line(sale_form, self.product, amount)
        sale = sale_form.save()
        return sale

    def test_group_max_weight(self):
        """
        Create a Sale order with first product
        Confirm the Sale Order
        Add a new product
        New move should be assigned to a new picking
        """
        self.product.weight = 6.0
        self.product_2.weight = 3.0
        self.product_3.weight = 9.0
        sale = self._get_new_sale_order(amount=1.0)
        sale.action_confirm()
        self.assertEqual(1, len(sale.picking_ids))
        self.assertEqual(2.0, sale.picking_ids.assignation_max_weight)
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_2, 1.0)
        self.assertEqual(2, len(sale.picking_ids))

        # Change the strategy, check if the number of pickings still == 2
        self.picking_type_out.group_pickings_maxweight = 0
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_3, 1.0)

        self.assertEqual(2, len(sale.picking_ids))

    def test_group_max_weight_several_quantities(self):
        """
        Create a Sale order with first product
        Confirm the Sale Order
        Add a new product (3.0)
        Weight is <= 8.0 (3 * 6.0)
        Add the same product (1.0)
        Weight is <= 8.0, same picking is used
        Add the same product (1.0)
        Weight is > 8.0, new picking is created
        Deactivate maximum weight
        The new move is affected to the same picking
        """
        self.product.weight = 2.0
        self.product_3.weight = 30.0
        sale = self._get_new_sale_order(amount=3.0)
        sale.action_confirm()
        # Check assignation max weight
        self.assertEqual(2.0, sale.picking_ids.assignation_max_weight)
        self.assertEqual(1, len(sale.picking_ids))

        # We can still add a product move with a weight <= 2.0
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product, 1.0)
        self.assertEqual(1, len(sale.picking_ids))
        self.assertEqual(8.0, sale.picking_ids.weight)

        # Picking max weight is set, the new move will go into a new picking
        self.assertEqual(0.0, sale.picking_ids.assignation_max_weight)
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product, 1.0)
        self.assertEqual(2, len(sale.picking_ids))

        # Change the strategy, check if the number of pickings still == 2
        self.picking_type_out.group_pickings_maxweight = 0
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_3, 1.0)

        self.assertEqual(2, len(sale.picking_ids))
