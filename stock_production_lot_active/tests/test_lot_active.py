# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestLotActive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_16")
        cls.product.write({"tracking": "lot"})
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def test_duplicate_inactive_lot(self):
        self.env["stock.production.lot"].create(
            {
                "name": "stock_production_lot_active lot",
                "product_id": self.product.id,
                "company_id": self.warehouse.company_id.id,
                "active": False,
            }
        )
        # it should not be possible to create a new lot with the same name and company
        # for the same product even when the first lot is inactive
        with self.assertRaises(ValidationError):
            self.env["stock.production.lot"].create(
                {
                    "name": "stock_production_lot_active lot",
                    "product_id": self.product.id,
                    "company_id": self.warehouse.company_id.id,
                    "active": True,
                }
            )
