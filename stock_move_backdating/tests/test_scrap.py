# Copyright 2024 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestScrap(TestCommon):
    def _create_scrap(self, product, qty=1.0, date_backdating=None):
        vals = {
            "product_id": product.id,
            "scrap_qty": qty,
            "location_id": self.stock_location.id,
            "product_uom_id": product.uom_id.id,
        }
        if date_backdating:
            vals["date_backdating"] = date_backdating
        return self.env["stock.scrap"].create(vals)

    def test_scrap_backdating(self):
        """Scrapping with a backdating date propagates it to the move line."""
        date_backdating = self._get_datetime_backdating(1)
        scrap = self._create_scrap(self.products[0], date_backdating=date_backdating)
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")
        move_line = scrap.move_ids.move_line_ids[:1]
        self.assertEqual(move_line.date_backdating, date_backdating)

    def test_scrap_onchange_future_date_raises(self):
        """Setting a future date_backdating on a scrap raises UserError."""
        future_date = self._get_datetime_backdating(-1)
        scrap = self._create_scrap(self.products[0])
        scrap.date_backdating = future_date
        with self.assertRaises(UserError):
            scrap.onchange_date_backdating()
