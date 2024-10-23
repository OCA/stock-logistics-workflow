# Copyright 2023 Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestStockScrapTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get sale order model
        cls.scrap_model = cls.env.ref("stock.model_stock_scrap")

        # Create users
        group_ids = (
            cls.env.ref("base.group_system") + cls.env.ref("stock.group_stock_manager")
        ).ids
        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "test@examlple.com",
            }
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.scrap_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('product_id', '!=', False)]",
            }
        )
        cls.product = cls.env.ref("product.product_product_6")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.scrap_location = cls.env["stock.location"].search(
            [("scrap_location", "=", True)], limit=1
        )

    def test_tier_validation_model_name(self):
        self.assertIn(
            "stock.scrap", self.tier_def_obj._get_tier_validation_model_names()
        )

    def test_validation_stock_scrap(self):
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "scrap_qty": 1.0,
                "location_id": self.location.id,
                "scrap_location_id": self.scrap_location.id,
            }
        )
        with self.assertRaises(ValidationError):
            scrap.action_validate()
        scrap.request_validation()
        scrap.invalidate_recordset()
        scrap.with_user(self.test_user_1).validate_tier()
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")

    def test_stock_picking_scrap(self):
        """Scrapping from picking does not open in a popup"""
        picking = self.env["stock.picking"].search([], limit=1)
        action = picking.button_scrap()
        self.assertFalse(action.get("target"))
