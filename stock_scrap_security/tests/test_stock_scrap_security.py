# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockScrapSecurity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Security Test Product",
                "type": "consu",
            }
        )
        cls.scrap_user = cls.env["res.users"].create(
            {
                "name": "Scrap User",
                "login": "scrap_user_test",
                "groups_id": [
                    Command.set(
                        [cls.env.ref("stock_scrap_security.group_stock_scrap_user").id]
                    )
                ],
            }
        )
        cls.scrap_manager = cls.env["res.users"].create(
            {
                "name": "Scrap Manager",
                "login": "scrap_manager_test",
                "groups_id": [
                    Command.set(
                        [
                            cls.env.ref(
                                "stock_scrap_security.group_stock_scrap_manager"
                            ).id
                        ]
                    )
                ],
            }
        )
        cls.standard_stock_user = cls.env["res.users"].create(
            {
                "name": "Standard Stock User",
                "login": "standard_stock_user_test",
                "groups_id": [Command.set([cls.env.ref("stock.group_stock_user").id])],
            }
        )

    def test_01_scrap_user_permissions(self):
        """Test that a standard Scrap User can create but not unlink."""
        scrap = (
            self.env["stock.scrap"]
            .with_user(self.scrap_user)
            .create(
                {
                    "product_id": self.product.id,
                    "scrap_qty": 1.0,
                }
            )
        )
        self.assertTrue(scrap, "Scrap User should be able to create scrap records.")
        with self.assertRaises(
            AccessError, msg="Scrap User should not be able to delete records."
        ):
            scrap.with_user(self.scrap_user).unlink()

    def test_02_scrap_manager_permissions(self):
        """Test that a Scrap Manager has full access including deletion."""
        scrap = (
            self.env["stock.scrap"]
            .with_user(self.scrap_manager)
            .create(
                {
                    "product_id": self.product.id,
                    "scrap_qty": 5.0,
                }
            )
        )
        self.assertTrue(scrap, "Scrap Manager should be able to create records.")
        res = scrap.with_user(self.scrap_manager).unlink()
        self.assertTrue(res, "Scrap Manager should be able to delete records.")

    def test_03_revoked_stock_permissions(self):
        """Test that a standard Stock User can no longer create scraps."""
        with self.assertRaises(
            AccessError,
            msg="Standard Stock User should have its scrap creation rights revoked.",
        ):
            self.env["stock.scrap"].with_user(self.standard_stock_user).create(
                {
                    "product_id": self.product.id,
                    "scrap_qty": 1.0,
                }
            )
