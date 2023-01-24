# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.tests.common import TransactionCase

from .common import TestPickingBackorder


class TestPickingBackorder(TestPickingBackorder, TransactionCase):

    _flow = "purchase"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_picking()

    def test_picking_backorder_strategy(self):
        # Default one one partner is "create" for purchase
        # Check picking partner backorder strategy
        self.assertEqual("create", self.picking.backorder_reason_strategy)
        self.partner.purchase_reason_backorder_strategy = "cancel"
        self.assertEqual("cancel", self.picking.backorder_reason_strategy)
        self.picking.picking_type_id.backorder_reason = False
        self.assertFalse(self.picking.backorder_reason_strategy)

    def test_purchase_picking_backorder_create_backorder_cancel(self):
        self.backorder_action = "create"
        self.purchase_backorder = "cancel"

        self._check_backorder_behavior()

    def test_purchase_picking_backorder_create_backorder_create(self):
        self.backorder_action = "create"
        self.purchase_backorder = "create"

        self._check_backorder_behavior()

    def test_purchase_picking_backorder_create_backorder_action_cancel(self):
        self.backorder_action = "cancel"
        self.purchase_backorder = "cancel"

        self._check_backorder_behavior()

    def test_purchase_picking_backorder_create_backorder_action_cancel_purchase_create(
        self,
    ):
        self.backorder_action = "cancel"
        self.purchase_backorder = "create"

        self._check_backorder_behavior()

    def test_purchase_picking_backorder_create_backorder_partner_cancel(self):
        self.backorder_action = "use_partner_option"
        self.purchase_backorder = "cancel"

        self._check_backorder_behavior()

    def test_purchase_picking_backorder_create_backorder_partner_create(self):
        self.backorder_action = "use_partner_option"
        self.purchase_backorder = "create"

        self._check_backorder_behavior()
