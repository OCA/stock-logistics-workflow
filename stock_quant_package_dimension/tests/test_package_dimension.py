# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import SavepointCase


class TestStockQuantPackageProductPackaging(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockQuantPackageProductPackaging, cls).setUpClass()
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "10 pack",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "qty": 10,
                "lngth": 12,
                "width": 13,
                "height": 14,
                "max_weight": 15,
            }
        )
        cls.package = cls.env["stock.quant.package"].create({})

    def assertRecordValues(self, records, expected_values):
        # a naive backport from 13.0 to ease the comparison of the code
        # between this backport into 10.0 from 13.0
        for record, values in zip(records, expected_values):
            for field, value in values.items():
                self.assertEqual(record[field], value)

    def test_set_dimensions_on_write(self):
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(
            self.package, [{"lngth": 12, "width": 13, "height": 14, "pack_weight": 15}]
        )

    def test_set_dimensions_on_write_no_override(self):
        values = {"lngth": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        self.package.with_context(
            _auto_assign_packaging=True
        ).product_packaging_id = self.packaging
        self.assertRecordValues(self.package, [values])

    def test_set_dimensions_onchange(self):
        values = {"lngth": 22, "width": 23, "height": 24, "pack_weight": 25}
        self.package.write(values)
        new_values = values.copy()
        new_values["product_packaging_id"] = self.packaging.id
        res = self.package.onchange(
            new_values,
            ["product_packaging_id"],
            {"product_packaging_id": "1"}
        )
        self.package.update(res.get("value", {}))
        # onchange overrides values
        self.assertRecordValues(
            self.package, [{"lngth": 12, "width": 13, "height": 14, "pack_weight": 15}]
        )
