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
        cls.test_user = new_test_user(
            cls.env,
            name="Test User",
            login="test_user",
            groups="base.group_system,stock.group_stock_user",
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
                "reviewer_id": cls.test_user.id,
                "definition_domain": "[('state', '=', 'assigned')]",
            }
        )
        cls.product = cls.product_model.create(
            {
                "name": "test_product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "type": "consu",
                "is_storable": True,
                "standard_price": 1.0,
                "list_price": 1.0,
            }
        )

    def _create_picking(self, picking_type, location, location_dest):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": location.id,
                "quantity": 10,
            }
        )
        picking = self.stock_picking_model.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
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

    def _run_tier_validation_flow(self, picking_type, location_from, location_to):
        picking = self._create_picking(picking_type, location_from, location_to)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state, "assigned", "the picking is not assigned")
        msg_error_received = (
            r"(?s)This action needs to be validated for at least one record.\s+"
            r"Please request a validation."
        )
        with self.assertRaisesRegex(ValidationError, msg_error_received):
            picking.button_validate()

        picking.request_validation()
        picking.invalidate_model()
        msg_error_open = (
            r"(?s)A validation process is still open for at least one record\."
        )
        with self.assertRaisesRegex(ValidationError, msg_error_open):
            picking.button_validate()
        picking = picking.with_user(self.test_user)
        picking.validate_tier()
        picking.invalidate_model()
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_tier_validation_picking_in(self):
        self._run_tier_validation_flow(
            self.picking_type_in, self.location_supplier, self.location_stock
        )

    def test_tier_validation_picking_out(self):
        self._run_tier_validation_flow(
            self.picking_type_out, self.location_stock, self.location_customer
        )
