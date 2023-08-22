# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase, tagged

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@tagged("post_install", "-at_install")
class TestStockPickingTierValidation(TransactionCase):
    def setUp(self):
        super(TestStockPickingTierValidation, self).setUp()
        self.stock_picking_model = self.env["stock.picking"]
        self.partner = self.env.ref("base.res_partner_2")
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.src_location = self.env.ref("stock.stock_location_stock")
        self.cust_location = self.env.ref("stock.stock_location_customers")
        self.product = self.env.ref("product.product_product_25")

    @classmethod
    def setUpClass(cls):
        super(TestStockPickingTierValidation, cls).setUpClass()

        setup_test_model(cls.env, [TierValidationTester])

        cls.test_model = cls.env[TierValidationTester._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )

        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        # Create users:
        group_ids = cls.env.ref("base.group_system").ids
        cls.test_user_1 = cls.env["res.users"].create(
            {"name": "John", "login": "test1", "groups_id": [(6, 0, group_ids)]}
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester])
        super(TestStockPickingTierValidation, cls).tearDownClass()

    def _create_move(self, picking, product, quantity=1.0):
        src_location = self.env.ref("stock.stock_location_stock")
        dest_location = self.env.ref("stock.stock_location_customers")
        return self.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": quantity,
                "quantity_done": quantity,
                "product_uom": product.uom_id.id,
                "location_id": src_location.id,
                "location_dest_id": dest_location.id,
            }
        )

    def test_01_tier_definition_models(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("stock.picking", res)

    def test_02_button_validate_success(self):
        # Test the successful validation scenario
        picking = self.stock_picking_model.create(
            {
                # Set up the required fields for testing
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.src_location.id,
                "location_dest_id": self.cust_location.id,
                "need_validation": False,
            }
        )
        self._create_move(picking, self.product)
        # Call the button_validate method and ensure it completes without raising an exception
        picking.button_validate()
