# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ProductProduct = self.env["product.product"]
        self.ProductTemplate = self.env["product.template"]
        self.uom_kg = self.browse_ref("uom.product_uom_kgm")
        self.uom_ton = self.browse_ref("uom.product_uom_ton")

    def _test_create_write(self, model):
        item = model.create({
            "name": "Demo Product",
            "uom_id": self.uom_kg.id,
            "uom_po_id": self.uom_kg.id,
        })
        self.assertEqual(item.weight, 1.0)
        item.uom_id = self.uom_ton
        self.assertEqual(item.weight, 1000.0)

    def test_create_product_product(self):
        self._test_create_write(self.ProductProduct)

    def test_create_product_template(self):
        self._test_create_write(self.ProductTemplate)

    def _test_onchange(self, model):
        f = Form(model)
        self.assertEqual(f.weight, 0.0)
        f.uom_id = self.uom_kg
        self.assertEqual(f.weight, 1.0)
        f.uom_id = self.uom_ton
        self.assertEqual(f.weight, 1000.0)

    def test_onchange_product_product(self):
        self._test_onchange(self.ProductProduct)

    def test_onchange_product_template(self):
        self._test_onchange(self.ProductTemplate)
