# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockReturnPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    @classmethod
    def _create_picking(cls, location, destination_location, picking_type):
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": destination_location.id,
            }
        )

    def test_00(self):
        """
        Data:
            4 stock location: customer, supplier, stock and stock_output
        Case:
            Create as much pickings as picking_type combinations to verify the compute
        Result:
            The picking_kind is correct for the combination of locations:
                supplier-stock: supplier_in
                stock-supplier: supplier_return
                customer_stock: customer_return
                stock-customer: customer_out
                supplier-customer: drop_shipping
                customer-supplier: drop_shipping_return
                stock-output: False
        """
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        self.assertEqual(picking.picking_kind, "supplier_in")
        picking = self._create_picking(
            self.stock_location, self.supplier_location, self.picking_type_out
        )
        self.assertEqual(picking.picking_kind, "supplier_return")
        picking = self._create_picking(
            self.customer_location, self.stock_location, self.picking_type_in
        )
        self.assertEqual(picking.picking_kind, "customer_return")
        picking = self._create_picking(
            self.stock_location, self.customer_location, self.picking_type_out
        )
        self.assertEqual(picking.picking_kind, "customer_out")
        picking = self._create_picking(
            self.supplier_location, self.customer_location, self.picking_type_out
        )
        self.assertEqual(picking.picking_kind, "drop_shipping")
        picking = self._create_picking(
            self.customer_location, self.supplier_location, self.picking_type_in
        )
        self.assertEqual(picking.picking_kind, "drop_shipping_return")
        picking = self._create_picking(
            self.stock_location, self.output_location, self.picking_type_out
        )
        self.assertFalse(picking.picking_kind)
