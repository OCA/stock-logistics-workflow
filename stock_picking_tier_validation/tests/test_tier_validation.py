# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common
from odoo.tests.common import tagged
from odoo.exceptions import UserError

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@tagged("post_install", "-at_install")
class TestStockPickingTierValidation(common.SavepointCase):
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

        cls.product = cls.env['product.product'].create({
            'default_code': 'TEST',
            'name': 'Test Produto',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_1').id,
            'list_price': 100.0,
            'standard_price': 70.0,
            'uom_id': cls.env.ref('uom.product_uom_kgm').id,
            'uom_po_id': cls.env.ref('uom.product_uom_kgm').id,
        })
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id,
            'move_lines': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 20.0,
                'product_uom': cls.env.ref('uom.product_uom_kgm').id,
                'location_id': cls.env.ref('stock.stock_location_stock').id,
                'location_dest_id': cls.env.ref('stock.stock_location_customers').id,
                'picking_type_id': cls.env.ref('stock.picking_type_out').id})]
        })

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester])
        super(TestStockPickingTierValidation, cls).tearDownClass()

    def test_01_tier_definition_models(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("stock.picking", res)

    def test_button_validate_success(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_lines.quantity_done = 6.0
        self.picking.review_ids = [(0, 0, {
            "name": "Test Review",
            "status": "pending",
        })]
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "confirmed")

    def test_button_validate_no_items(self):
        with self.assertRaises(UserError):
            self.picking.button_validate()

    def test_button_validate_without_review(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_lines.quantity_done = 20.0
        self.assertEqual(self.picking.button_validate(), None)

    def test_button_validate_with_review(self):
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )
        self.test_model.create({"test_field": 2.5})
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_lines.quantity_done = 20.0
        reviews = self.picking.request_validation()
        self.picking._validate_tier(reviews)
        self.picking.button_validate()
        self.assertEqual(self.picking.validated, False)

    def test_button_validate_with_multiple_reviews(self):
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )
        self.test_model.create({"test_field": 2.5})
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '<', 1.0)]",
            }
        )
        self.test_model.create({"test_field": 0.5})
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_lines.quantity_done = 20.0
        reviews = self.picking.request_validation()
        self.picking._validate_tier(reviews)
        self.assertEqual(self.picking.validated, False)
