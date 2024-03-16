# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_picking_group_by_partner_by_carrier.tests.common import (
    TestGroupByBase,
)


class TestGroupCustomerByBase(TestGroupByBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.env.ref("stock.picking_type_out").group_pickings_by_customer = True
