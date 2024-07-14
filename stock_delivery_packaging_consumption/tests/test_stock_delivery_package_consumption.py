from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestStockDeliveryPackagingConsumption(TransactionCase):
    def setUp(self):
        super().setUp()

        # create products and quants
        self.phone_product = self.env["product.product"].create(
            {
                "name": "The new mobile phone",
                "type": "product",
            }
        )
        self.shipping_product = self.env["product.product"].create(
            {
                "name": "Shipping",
                "type": "service",
            }
        )
        self.packaging_product_1 = self.env["product.product"].create(
            {
                "name": "Palette A",
                "type": "product",
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.packaging_product_1.id,
                "inventory_quantity": 10,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        ).action_apply_inventory()
        self.packaging_product_2 = self.env["product.product"].create(
            {
                "name": "Palette B",
                "type": "product",
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.packaging_product_2.id,
                "inventory_quantity": 5,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        ).action_apply_inventory()
        self.package_type_a = self.env["stock.package.type"].create(
            {
                "package_carrier_type": "none",
                "name": "Palette A",
                "product_id": self.packaging_product_1.id,
                "width": 60,
                "height": 60,
                "packaging_length": 60,
            }
        )
        self.package_type_b = self.env["stock.package.type"].create(
            {
                "package_carrier_type": "none",
                "name": "Palette B",
                "product_id": self.packaging_product_2.id,
                "width": 60,
                "height": 60,
                "packaging_length": 60,
            }
        )
        self.package_type_c = self.env["stock.package.type"].create(
            {
                "package_carrier_type": "none",
                "name": "Box without quants",
                "width": 60,
                "height": 60,
                "packaging_length": 60,
            }
        )
        self.carrier = self.env["delivery.carrier"].create(
            {
                "name": "Test Carrier",
                "delivery_type": "fixed",
                "product_id": self.shipping_product.id,
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Customer - test"})
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.phone_product.name,
                            "product_id": self.phone_product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.phone_product.uom_id.id,
                            "price_unit": 100.00,
                        }
                    )
                ],
            }
        )
        sale_order.carrier_id = self.carrier.id
        sale_order.action_confirm()
        self.picking = sale_order.picking_ids.filtered(
            lambda pick: pick.picking_type_code == "outgoing"
        )

    def test_simple_packaging_consumption(self):
        """Test one package for the delivery"""
        quant_packaging_1_before = self.packaging_product_1.quantity_svl

        # Put in pack
        self.picking.move_ids[0].quantity = 5
        self.picking.move_ids[0].picked = True
        move_lines_to_pack = self.picking._package_move_lines()
        self.picking._pre_put_in_pack_hook(move_lines_to_pack)
        package = self.picking._put_in_pack(move_lines_to_pack)
        package.package_type_id = self.package_type_a.id
        # Confirm picking
        self.picking.button_validate()

        quant_packaging_1_after = self.packaging_product_1.quantity_svl
        # One package was used, the new quantity should be minus 1
        self.assertEqual(quant_packaging_1_after, quant_packaging_1_before - 1)

    def test_complex_packaging_consumption(self):
        """Test two packages of type a, one of type b for the delivery"""

        quant_packaging_1_before = self.packaging_product_1.quantity_svl
        quant_packaging_2_before = self.packaging_product_2.quantity_svl

        # Put in first pack
        self.picking.move_ids[0].quantity = 1
        move_lines_to_pack = self.picking._package_move_lines()
        self.picking._pre_put_in_pack_hook(move_lines_to_pack)
        package_1 = self.picking._put_in_pack(move_lines_to_pack)
        package_1.package_type_id = self.package_type_a.id

        # Put in second pack
        self.picking.move_ids[0].quantity = 3
        move_lines_to_pack = self.picking._package_move_lines()
        self.picking._pre_put_in_pack_hook(move_lines_to_pack)
        package_2 = self.picking._put_in_pack(move_lines_to_pack)
        package_2.package_type_id = self.package_type_a.id

        # Put in third pack
        self.picking.move_ids[0].quantity = 5
        self.picking.move_ids[0].picked = True
        move_lines_to_pack = self.picking._package_move_lines()
        self.picking._pre_put_in_pack_hook(move_lines_to_pack)
        package_3 = self.picking._put_in_pack(move_lines_to_pack)
        package_3.package_type_id = self.package_type_b.id

        # Confirm picking
        self.picking.button_validate()

        quant_packaging_1_after = self.packaging_product_1.quantity_svl
        quant_packaging_2_after = self.packaging_product_2.quantity_svl

        # two packages of first packaging material were used,
        # the new quantity should be minus 2
        self.assertEqual(quant_packaging_1_after, quant_packaging_1_before - 2)
        # one packages of second packaging material were used,
        # the new quantity should be minus 1
        self.assertEqual(quant_packaging_2_after, quant_packaging_2_before - 1)

    def test_no_packaging_consumption(self):
        """Test no package consumption when put in pack package has
        no product id for the delivery"""
        quant_packaging_1_before = self.packaging_product_1.quantity_svl
        quant_packaging_2_before = self.packaging_product_2.quantity_svl

        # Put in pack
        self.picking.move_ids[0].quantity = 5
        self.picking.move_ids[0].picked = True
        move_lines_to_pack = self.picking._package_move_lines()
        self.picking._pre_put_in_pack_hook(move_lines_to_pack)
        package = self.picking._put_in_pack(move_lines_to_pack)
        package.package_type_id = self.package_type_c.id
        # Confirm picking
        self.picking.button_validate()

        quant_packaging_1_after = self.packaging_product_1.quantity_svl
        quant_packaging_2_after = self.packaging_product_2.quantity_svl
        # One package without linked product was used, the amount stays the same
        self.assertEqual(quant_packaging_1_after, quant_packaging_1_before)
        self.assertEqual(quant_packaging_2_after, quant_packaging_2_before)
