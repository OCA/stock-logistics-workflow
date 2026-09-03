# Copyright 2026 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestStockLocationInventory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.next_inventory_date = fields.Date.end_of(fields.Date.today(), "year")
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Location Inventory Validation Test",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "Location test user",
                "login": "location_test_user",
                "groups_id": [Command.set([cls.env.ref("stock.group_stock_user").id])],
            }
        )
        cls.group = cls.env.ref(
            "stock_location_validate_inventory.group_stock_location_can_validate_inventory"
        )

    def test_no_right(self):
        with self.assertRaises(
            UserError,
            msg="You are not allowed to validate the location inventory",
        ):
            self.location.with_user(self.user).validate_inventory()
        self.assertFalse(self.location.last_inventory_date)

    def test_empty_location(self):
        self.user.groups_id = [Command.link(self.group.id)]
        self.assertFalse(self.location.last_inventory_date)
        self.location.with_user(self.user).validate_inventory()
        self.assertEqual(self.location.last_inventory_date, fields.Date.today())

    def test_location_with_stock(self):
        self.user.groups_id = [Command.link(self.group.id)]
        product = self.env["product.product"].create(
            {
                "name": "Product test",
                "type": "product",
            }
        )
        quant = (
            self.env["stock.quant"]
            .sudo()
            .create(
                {
                    "product_id": product.id,
                    "quantity": 10.0,
                    "location_id": self.location.id,
                }
            )
        )
        self.assertFalse(quant.last_count_date)
        self.assertFalse(self.location.last_inventory_date)
        self.location.with_user(self.user).validate_inventory()
        # Here odoo doesn't update the last_count_date when there is no difference
        self.assertEqual(quant.last_count_date, False)
        self.assertEqual(quant.inventory_date, self.next_inventory_date)
