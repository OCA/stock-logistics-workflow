# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestDeliveryPackageDefaultShippingWeight(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Delivery package", "package_default_shipping_weight": 10.0}
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def test_check_negative_value(self):
        with self.assertRaises(ValidationError):
            self.packaging.package_default_shipping_weight = -1

    def test_default_weight(self):
        picking = self.env["stock.picking"].search(
            [
                ("picking_type_id", "=", self.picking_type_out.id),
                ("state", "=", "assigned"),
            ],
            limit=1,
        )
        move_line = fields.first(picking.move_line_ids_without_package)
        move_line.qty_done = move_line.product_uom_qty
        picking.put_in_pack()
        package = move_line.result_package_id
        self.assertAlmostEqual(package.shipping_weight, 0.0)
        package.packaging_id = self.packaging
        self.assertAlmostEqual(
            package.shipping_weight, self.packaging.package_default_shipping_weight
        )
