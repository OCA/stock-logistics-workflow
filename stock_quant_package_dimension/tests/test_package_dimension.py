# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from . import common


class TestStockQuantPackageProductPackaging(common.TestStockQuantPackageCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.packaging_ids = cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "10 pack",
                "product_id": cls.product.id,
                "qty": 10,
                "packaging_length": 12,
                "width": 13,
                "height": 14,
                "weight": 15,
            }
        )
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

    def test_package_estimated_pack_weight_kg(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            7.0,
            package_id=self.package,
        )
        # Weight are taken from product, like the delivery module
        self.assertEqual(self.package.estimated_pack_weight_kg, 7)
        self.move._action_assign()
        self.assertEqual(
            self.package.with_context(
                picking_id=self.move.picking_id.id
            ).estimated_pack_weight_kg,
            7,
        )
