# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, common, tagged


@tagged("post_install", "-at_install")
class TestStockLotScrap(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "is_storable": True}
        )
        cls.company = cls.env.ref("base.main_company")
        cls.lot010 = cls.env["stock.lot"].create(
            {
                "name": "0000010",
                "product_id": cls.product.id,
                "company_id": cls.company.id,
            }
        )
        cls.quant1 = cls.env["stock.quant"].create(
            {
                "quantity": 5000.0,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "product_id": cls.product.id,
                "lot_id": cls.lot010.id,
            }
        )
        cls.quant2 = cls.env["stock.quant"].create(
            {
                "quantity": 325.0,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "product_id": cls.product.id,
                "lot_id": cls.lot010.id,
            }
        )
        # Make sure the user is in English
        cls.env.user.lang = "en_US"

    def test_picking_created(self):
        Form(self.lot010)
        res = self.lot010.action_scrap_lot()
        self.assertIn("domain", res)
        scraps = self.env["stock.move"].search(res["domain"])
        self.assertEqual(len(scraps), 2)
        self.assertTrue(all(scraps.mapped("is_scrap")))
        self.assertFalse(scraps.filtered(lambda m: m.state in ("done", "cancel")))
        self.assertAlmostEqual(sum(scraps.mapped("quantity")), 5325)
        self.assertEqual(scraps.lot_ids, self.lot010)
        scrap = scraps.filtered(lambda m: m.quantity == 325)
        scrap.action_scrap()
        self.assertEqual(scrap.state, "done")
        self.assertIn("Lot was scrapped by", self.lot010.message_ids[:1].body)
        self.assertAlmostEqual(self.lot010.product_qty, 5000)

    def test_warning(self):
        product_new = self.product.create({"name": "Test product 040"})
        self.lot040 = self.env["stock.lot"].create(
            {
                "name": "0000040",
                "product_id": product_new.id,
                "company_id": self.company.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.lot040.action_scrap_lot()
