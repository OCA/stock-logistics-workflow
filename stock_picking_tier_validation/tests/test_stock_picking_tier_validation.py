# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingTierValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "Test User 1",
                "login": "test1",
                "email": "test1@example.com",
                "groups_id": [(6, 0, cls.env.ref("base.group_system").ids)],
            }
        )
        cls.test_user_2 = cls.env["res.users"].create(
            {"name": "Test User 2", "login": "test2", "email": "test2@example.com"}
        )
        picking_model = cls.env["ir.model"].search([("model", "=", "stock.picking")])
        cls.env["tier.definition"].create(
            {
                "model_id": picking_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[]",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Storable product", "type": "product"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": "incoming move",
                "product_id": cls.product.id,
                "product_uom_qty": 3.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.picking.action_confirm()

    def test_01_check_tier_review(self):
        res_dict = self.picking.button_validate()
        wizard = self.env[(res_dict.get("res_model"))].browse(res_dict.get("res_id"))
        with self.assertRaises(ValidationError):
            wizard.process()

    def test_02_check_tier_review(self):
        reviews = self.picking.sudo(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.picking.sudo(self.test_user_1.id)
        record.validate_tier()
        self.assertTrue(record.validated)
        res_dict = self.picking.button_validate()
        wizard = self.env[(res_dict.get("res_model"))].browse(res_dict.get("res_id"))
        wizard.process()
