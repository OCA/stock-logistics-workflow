# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)shipping_weight
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDeliveryPackageDefaultShippingWeight(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.packaging = cls.env["stock.package.type"].create(
            {"name": "Delivery package", "package_default_shipping_weight": 10.0}
        )
        cls.new_packaging = cls.env["stock.package.type"].create(
            {"name": "Delivery package", "package_default_shipping_weight": 12.0}
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
        picking.action_put_in_pack()
        package = move_line.result_package_id
        self.assertAlmostEqual(package.shipping_weight, 0.0)
        package.package_type_id = self.packaging
        self.assertAlmostEqual(
            package.shipping_weight, self.packaging.package_default_shipping_weight
        )

    def test_onchange_package_type_id(self):
        picking = self.env["stock.picking"].search(
            [
                ("picking_type_id", "=", self.picking_type_out.id),
                ("state", "=", "assigned"),
            ],
            limit=1,
        )
        move_line = fields.first(picking.move_line_ids_without_package)
        picking.action_put_in_pack()
        package = move_line.result_package_id
        package.package_type_id = self.packaging
        package.package_type_id = self.new_packaging
        self.assertAlmostEqual(
            package.shipping_weight,
            package.package_type_id.package_default_shipping_weight,
        )
