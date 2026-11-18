# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create({"name": "Test Company 2"})

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        cls.template = cls.product.product_tmpl_id

    def test_calculate_creates_stock_company_records(self):
        """_calculate_stock_for_product creates record on
        stock.company for each company."""
        StockCompany = self.env["stock.company"].sudo()
        StockCompany._calculate_stock_for_product(self.product)

        companies = self.env["res.company"].search([])
        for company in companies:
            rec = StockCompany.search(
                [
                    ("product_id", "=", self.product.id),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            self.assertTrue(
                rec,
                f"Need to exist record stock.company for the company {company.name}",
            )

    def test_calculate_does_not_duplicate_records(self):
        """Calling _calculate_stock_for_product two times without twice the records."""
        StockCompany = self.env["stock.company"].sudo()
        StockCompany._calculate_stock_for_product(self.product)
        StockCompany._calculate_stock_for_product(self.product)

        companies = self.env["res.company"].search([])
        for company in companies:
            count = StockCompany.search_count(
                [
                    ("product_id", "=", self.product.id),
                    ("company_id", "=", company.id),
                ]
            )
            self.assertEqual(
                count,
                1,
                f"There should be no duplicates for the company {company.name}",
            )

    def test_calculate_updates_quantity(self):
        """_calculate_stock_for_product updates quantity_available
        if the record exists."""
        StockCompany = self.env["stock.company"].sudo()

        StockCompany.create(
            {
                "product_id": self.product.id,
                "company_id": self.company_1.id,
                "quantity_available": 0.0,
            }
        )

        rec_before = StockCompany.search(
            [
                ("product_id", "=", self.product.id),
                ("company_id", "=", self.company_1.id),
            ],
            limit=1,
        )
        rec_before.quantity_available = 99.0

        StockCompany._calculate_stock_for_product(self.product)

        rec_after = StockCompany.search(
            [
                ("product_id", "=", self.product.id),
                ("company_id", "=", self.company_1.id),
            ],
            limit=1,
        )
        self.assertEqual(
            rec_after.quantity_available,
            self.product.with_context(
                allowed_company_ids=[self.company_1.id]
            ).qty_available,
        )

    def test_compute_stock_by_company_ids_on_product(self):
        """stock_by_company_ids in product.product returns records
        for all companies."""
        companies = self.env["res.company"].search([])
        records = self.product.stock_by_company_ids
        company_ids_in_result = records.mapped("company_id").ids
        for company in companies:
            self.assertIn(
                company.id,
                company_ids_in_result,
                f"The company {company.name} is missing from"
                "the product's stock_by_company_ids",
            )

    def test_compute_stock_by_company_ids_correct_product(self):
        """stock_by_company_ids contains only records for the correct product."""
        for rec in self.product.stock_by_company_ids:
            self.assertEqual(
                rec.product_id.id,
                self.product.id,
                "stock.company is pointing to the wrong product",
            )

    def test_template_stock_by_company_ids_empty_for_service(self):
        """For a service product, stock_by_company_ids must be empty."""
        service = self.env["product.product"].create(
            {
                "name": "Servicie Test",
                "type": "service",
            }
        )
        self.assertFalse(
            service.product_tmpl_id.stock_by_company_ids,
            "A service product should not have stock_by_company_ids",
        )

    def test_stock_company_uom_related(self):
        """The uom_id in stock.company must match the product's uom."""
        StockCompany = self.env["stock.company"].sudo()
        StockCompany._calculate_stock_for_product(self.product)
        rec = StockCompany.search(
            [
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        self.assertEqual(
            rec.uom_id,
            self.product.uom_id,
            "The uom_id in stock.company does not match the product's uom_id",
        )
