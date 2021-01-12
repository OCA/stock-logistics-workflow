# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestStockLotScrap(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product"}
        )
        cls.company = cls.env.ref("base.main_company")
        cls.lot010 = cls.env["stock.production.lot"].create(
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
        res = self.lot010.action_scrap_lot()
        self.assertIn("domain", res)
        scrap = self.env["stock.scrap"].search(safe_eval(res["domain"]))
        self.assertAlmostEqual(sum(scrap.mapped("scrap_qty")), 5325)
        self.assertTrue(
            all(scrap.mapped("move_id").mapped(lambda x: x.state == "done"))
        )
        scrap[:1].action_validate()
        self.assertIn("Lot was scrapped by", self.lot010.message_ids[:1].body)

    def test_warning(self):
        product_new = self.product.create({"name": "Test product 040"})
        self.lot040 = self.env["stock.production.lot"].create(
            {
                "name": "0000040",
                "product_id": product_new.id,
                "company_id": self.company.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.lot040.action_scrap_lot()
