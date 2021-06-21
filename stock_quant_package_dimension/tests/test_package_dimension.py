# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, SavepointCase


class TestStockQuantPackageProductPackaging(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "10 pack",
                "product_id": cls.product.id,
                "qty": 10,
                "packaging_length": 12,
                "width": 13,
                "height": 14,
                "max_weight": 15,
            }
        )
        cls.package = cls.env["stock.quant.package"].create({})
        cls.uom_cm = cls.env["uom.uom"].search([("name", "=", "cm")], limit=1)

    def test_set_dimensions_on_write(self):
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(
            self.package,
            [{"pack_length": 12, "width": 13, "height": 14, "pack_weight": 15}],
        )

    def test_set_dimensions_on_write_no_override(self):
        values = {"pack_length": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(self.package, [values])

    def test_set_dimensions_onchange(self):
        values = {"pack_length": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        with Form(self.package) as form:
            form.product_packaging_id = self.packaging
            form.save()
        # onchange overrides values
        self.assertRecordValues(
            self.package,
            [{"pack_length": 12, "width": 13, "height": 14, "pack_weight": 15}],
        )
