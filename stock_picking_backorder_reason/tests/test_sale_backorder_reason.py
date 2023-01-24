# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase

from .common import TestPickingBackorder


class TestSalePickingBackorder(TestPickingBackorder, TransactionCase):

    _flow = "sale"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_picking()

    def test_picking_backorder_strategy(self):
        # Check picking partner backorder strategy
        self.assertEqual("cancel", self.picking.backorder_reason_strategy)
        self.partner.sale_reason_backorder_strategy = "create"
        self.assertEqual("create", self.picking.backorder_reason_strategy)
        self.picking.picking_type_id.backorder_reason = False
        self.assertFalse(self.picking.backorder_reason_strategy)

    def test_sale_picking_backorder_create_backorder_cancel(self):
        self.backorder_action = "create"
        self.sale_backorder = "cancel"

        self._check_backorder_behavior()

    def test_sale_picking_backorder_create_backorder_create(self):
        self.backorder_action = "create"
        self.sale_backorder = "create"

        self._check_backorder_behavior()

    def test_sale_picking_backorder_create_backorder_action_cancel(self):
        self.backorder_action = "cancel"
        self.sale_backorder = "cancel"

        self._check_backorder_behavior()

    def test_sale_picking_backorder_create_backorder_action_cancel_sale_create(self):
        self.backorder_action = "cancel"
        self.sale_backorder = "create"

        self._check_backorder_behavior()

    def test_sale_picking_backorder_create_backorder_partner_cancel(self):
        self.backorder_action = "use_partner_option"
        self.sale_backorder = "cancel"

        self._check_backorder_behavior()

    def test_sale_picking_backorder_create_backorder_partner_create(self):
        self.backorder_action = "use_partner_option"
        self.sale_backorder = "create"

        self._check_backorder_behavior()
