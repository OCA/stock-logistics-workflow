# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tests.common import tagged

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@tagged("post_install", "-at_install")
class TestStockPickingTierValidation(common.SavepointCase):
    def setUp(self):
        super(TestStockPickingTierValidation, self).setUp()
        self.stock_picking_model = self.env["stock.picking"]

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

    def test_01_tier_definition_models(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("stock.picking", res)

    def test_02_button_validate_with_need_validation(self):
        picking = self.stock_picking_model.create(
            {
                # Set up the required fields for testing
                # ...
                "need_validation": True,
            }
        )
        with self.assertRaises(ValidationError) as context:
            picking.button_validate()
        self.assertIn(
            "This action needs to be validated for at least one record.",
            context.exception.args[0],
        )

    def test_03_button_validate_with_review_ids_not_validated(self):
        picking = self.stock_picking_model.create(
            {
                # Set up the required fields for testing
               # ...
               "review_ids": [(0, 0, {"validated": False})],
                "validated": False,
            }
        )
        with self.assertRaises(ValidationError) as context:
            picking.button_validate()
        self.assertIn(
            "A validation process is still open for at least one record.",
            context.exception.args[0],
        )

    def test_04_button_validate_success(self):
        # Test the successful validation scenario
        picking = self.stock_picking_model.create(
            {
            # Set up the required fields for testing
            # ...
            "need_validation": False,
            }
        )

        # Call the button_validate method and ensure it completes without raising an exception
        picking.button_validate()
