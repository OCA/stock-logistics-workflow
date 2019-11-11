# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockQuantPackageProductPackaging(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receipt_picking_type = cls.env.ref("stock.picking_type_in")
        # show_reserved must be set here because it changes the behaviour of
        # put_in_pack operation:
        # if show_reserved: qty_done must be set on stock.picking.move_line_ids
        # if not show_reserved: qty_done must be set on
        #   stock.picking.move_line_nosuggest_ids
        cls.receipt_picking_type.show_reserved = True
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "10 pack", "product_id": cls.product.id, "qty": 10}
        )

    def test_auto_assign_packaging(self):
        location_dest = self.receipt_picking_type.default_location_dest_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.receipt_picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": location_dest.id,
            }
        )
        picking.onchange_picking_type()
        picking.write(
            {
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "TEST",
                            "product_id": self.product.id,
                            "product_uom_qty": 30.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": picking.location_id.id,
                            "location_dest_id": picking.location_dest_id.id,
                        },
                    )
                ]
            }
        )
        picking.action_confirm()
        picking.move_line_ids.qty_done = 10.0
        first_package = picking.put_in_pack()
        picking.move_line_ids.filtered(
            lambda ml: not ml.result_package_id
        ).qty_done = 20.0
        second_package = picking.put_in_pack()
        picking.button_validate()
        self.assertEqual(first_package.single_product_id, self.product)
        self.assertEqual(first_package.single_product_qty, 10.0)
        self.assertEqual(second_package.single_product_id, self.product)
        self.assertEqual(second_package.single_product_qty, 20.0)
        self.assertEqual(first_package.product_packaging_id, self.packaging)
        self.assertFalse(second_package.product_packaging_id)
