# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockPickingTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.py_model = cls.env.ref("stock.model_stock_picking")
        cls.product_model = cls.env["product.product"]
        cls.reviewer = new_test_user(
            cls.env,
            name="Test User",
            login="test_user",
            groups="stock.group_stock_manager",
        )
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.stock_picking_model = cls.env["stock.picking"]
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.location_customer = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.tier_def_obj.create(
            {
                "model_id": cls.py_model.id,
                "review_type": "individual",
                "reviewer_id": cls.reviewer.id,
                "definition_domain": "[('state', '=', 'assigned')]",  # Added domain
            }
        )
        cls.product = cls.product_model.create(
            {
                "name": "test_product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "type": "product",
                "standard_price": 1.0,
                "list_price": 1.0,
            }
        )
        cls.picking_in = cls._create_picking(
            cls.picking_type_in, cls.location_supplier, cls.location_stock
        )
        cls.picking_in.action_confirm()
        cls.picking_in.action_assign()
        cls.picking_out = cls._create_picking(
            cls.picking_type_out, cls.location_stock, cls.location_customer
        )
        cls.picking_out.action_confirm()
        cls.picking_out.action_assign()

    @classmethod
    def _create_picking(cls, picking_type, location, location_dest):
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": location.id,
                "quantity": 10,
            }
        )
        picking = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move",
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 3,
                            "location_id": location.id,
                            "location_dest_id": location_dest.id,
                            "price_unit": 10,
                        }
                    ),
                ],
            }
        )
        return picking

    def test_tier_validation_picking_in(self):
        picking_in = self.picking_in
        self.assertEqual(picking_in.state, "assigned", "the picking is not assigned")
        picking_in.request_validation()
        self.assertTrue(
            len(picking_in.review_ids) == 1,
            msg="The picking should have a review after requesting validation.",
        )
        with self.assertRaises(
            ValidationError,
            msg="The picking should not be validated without tier validation.",
        ):
            picking_in.button_validate()
        picking_in.with_user(self.reviewer).validate_tier()
        picking_in.button_validate()
        self.assertEqual(picking_in.state, "done")

    def test_tier_validation_picking_out(self):
        picking_out = self.picking_out
        self.assertEqual(picking_out.state, "assigned", "The picking is not assigned.")

        # Now request validation
        picking_out.request_validation()

        self.assertTrue(
            len(picking_out.review_ids) == 1,
            msg="The picking should have a review after requesting validation.",
        )
        with self.assertRaises(
            ValidationError,
            msg="The picking should not be validated without tier validation.",
        ):
            picking_out.button_validate()
        picking_out.with_user(self.reviewer).validate_tier()
        picking_out.button_validate()
        self.assertEqual(picking_out.state, "done")
