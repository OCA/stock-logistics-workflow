# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPickingRestrictCancel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env.ref("product.product_product_5")
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner_1.id,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "location_id": cls.env.ref("stock.stock_location_stock").id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        }
                    )
                ],
            }
        )

    def test_stock_picking_restrict_cancel_printed_enabled(self):
        self.picking.printed = True
        with self.assertRaises(UserError):
            self.picking.action_cancel()

    def test_stock_picking_restrict_cancel_printed_disabled(self):
        self.picking_type.restrict_cancel_if_printed = False
        self.picking.printed = True
        self.picking.action_cancel()

    def test_stock_move_restrict_cancel_printed_enabled(self):
        self.picking.printed = True
        with self.assertRaises(UserError):
            self.picking.move_ids._action_cancel()

    def test_stock_move_restrict_cancel_printed_disabled(self):
        self.picking_type.restrict_cancel_if_printed = False
        self.picking.printed = True
        self.picking.move_ids._action_cancel()
