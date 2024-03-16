# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import first
from odoo.tests.common import TransactionCase

from .common import TestGroupCustomerByBase


class TestGroupBy(TestGroupCustomerByBase, TransactionCase):
    def test_sale_stock_dont_merge_different_customer(self):
        """
        Define a different customer than the shipping
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.partner_id = self.partner_2
        so2.partner_shipping_id = self.partner
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for the sales, and it is shared
        self.assertTrue(so1.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking mentions both sales names
        self.assertTrue(so1.name in first(so1.picking_ids).origin)
