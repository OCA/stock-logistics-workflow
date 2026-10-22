# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common


class TestAmountTotalCurrency(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")
        cls.eur.active = True
        cls.company = cls.env["res.company"].create(
            {"name": "LC USD Company", "currency_id": cls.usd.id}
        )
        cls.env = cls.env(
            context=dict(cls.env.context, allowed_company_ids=cls.company.ids)
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "LC Journal",
                "type": "general",
                "code": "LCUSD",
                "company_id": cls.company.id,
            }
        )
        cls.env["res.currency.rate"].create(
            {
                "name": "2019-01-01",
                "currency_id": cls.eur.id,
                "rate": 0.5,
                "company_id": cls.company.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Shipping Fee", "type": "service"}
        )

    def _create_landed_cost(self, currency):
        return self.env["stock.landed.cost"].create(
            {
                "date": "2019-01-01",
                "account_journal_id": self.journal.id,
                "currency_id": currency.id,
                "cost_lines": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "split_method": "equal",
                            "currency_price_unit": 100,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )

    def test_01_amount_total_company_currency(self):
        landed_cost = self._create_landed_cost(self.eur)
        self.assertEqual(landed_cost.currency_id, self.eur)
        self.assertEqual(landed_cost.company_currency_id, self.usd)
        self.assertEqual(landed_cost.amount_total, 200)
        field = landed_cost.fields_get(["amount_total"])["amount_total"]
        self.assertEqual(field["currency_field"], "company_currency_id")

    def test_02_amount_total_tracking_company_currency(self):
        landed_cost = self._create_landed_cost(self.eur)
        self.env.flush_all()
        self.env.cr.precommit.run()
        landed_cost.cost_lines.price_unit = 300
        self.env.flush_all()
        self.env.cr.precommit.run()
        tracking = landed_cost.message_ids.tracking_value_ids.filtered(
            lambda t: t.field.name == "amount_total"
        )
        self.assertTrue(tracking)
        self.assertEqual(tracking.currency_id, self.usd)

    def test_03_amount_total_rounded_with_company_currency(self):
        jpy = self.env.ref("base.JPY")
        jpy.active = True
        company = self.env["res.company"].create(
            {"name": "LC JPY Company", "currency_id": jpy.id}
        )
        journal = self.env["account.journal"].create(
            {
                "name": "LC JPY Journal",
                "type": "general",
                "code": "LCJPY",
                "company_id": company.id,
            }
        )
        landed_cost = (
            self.env["stock.landed.cost"]
            .with_company(company)
            .create(
                {
                    "date": "2019-01-01",
                    "account_journal_id": journal.id,
                    "currency_id": self.eur.id,
                    "cost_lines": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "split_method": "equal",
                                "currency_price_unit": 100,
                                "price_unit": 200.4,
                            },
                        )
                    ],
                }
            )
        )
        self.assertEqual(landed_cost.company_currency_id, jpy)
        self.assertEqual(landed_cost.amount_total, 200)

    def test_04_amount_total_same_currency(self):
        landed_cost = self._create_landed_cost(self.usd)
        self.assertEqual(landed_cost.currency_id, landed_cost.company_currency_id)
        self.assertEqual(landed_cost.amount_total, 200)
