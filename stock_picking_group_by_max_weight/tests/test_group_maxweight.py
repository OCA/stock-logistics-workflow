# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestGroupMaxWeight(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_init(self):
        self.env["stock.picking"].init()

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

    def test_group_max_weight_change_parameter(self):
        """
        Create a Sale order with first product
        Confirm the Sale Order
        Add a new product
        New move should be assigned to a new picking

        Create inventory quantity
        Assign the picking
        """
        self.product.weight = 6.0
        self.product_2.weight = 3.0
        self.product_3.weight = 9.0
        sale = self._get_new_sale_order(amount=1.0)
        sale.action_confirm()
        self.assertEqual(1, len(sale.picking_ids))
        picking_1 = sale.picking_ids
        self.assertEqual(2.0, sale.picking_ids.assignation_max_weight)
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_2, 1.0)
        self.assertEqual(2, len(sale.picking_ids))

        # Change the strategy, check if the number of pickings still == 2
        self.picking_type_out.group_pickings_maxweight = 0
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_3, 1.0)

        self.assertEqual(2, len(sale.picking_ids))

        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 50.0,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )._apply_inventory()

        picking_1.action_assign()
        self.assertEqual("assigned", picking_1.state)
        for line in picking_1.move_line_ids:
            line.qty_done = line.reserved_qty
        picking_1._action_done()

        self.picking_type_out.group_pickings_maxweight = 2.0

        self.assertEqual(2.0, picking_1.assignation_max_weight)

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

    def test_split_at_creation(self):
        """Test that a SO with 2 lines that will exceed the max weight if set into
        the same picking, will be split"""
        self.product.weight = 6.0
        self.product_2.weight = 3.0
        # the max weight is 8.0
        # we create a SO with 2 lines of 1.0 each ->
        # 2 pickings will be created since the weight is 9.0
        # the first picking will have a weight of 6.0
        sale = self._get_new_sale_order(amount=1.0)
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_2, 1.0)
        sale.action_confirm()
        self.assertEqual(2, len(sale.picking_ids))

    def test_no_split_if_one_move_exceed(self):
        """
        If the picking contains a move that exceed the max weight, the picking
        is not split
        """
        self.product.weight = 6.0
        sale = self._get_new_sale_order(amount=3.0)
        sale.action_confirm()
        self.assertEqual(1, len(sale.picking_ids))

    def test_multi_split_at_creation(self):
        self.product.weight = 6.0
        self.product_2.weight = 3.0
        self.product_3.weight = 3.0
        sale = self._get_new_sale_order(amount=1.0)
        with Form(sale) as sale_form:
            self._set_line(sale_form, self.product_2, 2.0)
            self._set_line(sale_form, self.product_3, 2.0)

        sale.action_confirm()
        self.assertEqual(3, len(sale.picking_ids))
