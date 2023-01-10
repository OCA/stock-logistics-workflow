# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPickingGroupBy(TransactionCase):
    def test_index(self):
        index_name = "stock_picking_groupby_key_index"
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,)
        )
        self.assertTrue(self.env.cr.fetchone())
