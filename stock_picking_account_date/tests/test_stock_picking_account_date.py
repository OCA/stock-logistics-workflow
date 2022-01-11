# © 2016-2021 Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo.tests.common import TransactionCase


class TestStockPickingAccountDate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref("product.product_product_4d")
        self.product_category = self.env.ref("product.product_category_5")
        self.product_category.write({"property_valuation": "real_time"})
        self.partner = self.env.ref("base.res_partner_address_15")
        self.date = date.today() - timedelta(days=1)

    def test_01_picking_account_date(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 4,
                        },
                    )
                ],
            }
        )
        order.button_confirm()
        pickings = order.picking_ids
        pickings.write(
            {
                "accounting_date": self.date,
            }
        )
        pickings.action_set_quantities_to_reservation()
        pickings.button_validate()
        move = self.env["account.move"].search([("ref", "ilike", pickings.name)])
        self.assertEqual(move.date, self.date)
