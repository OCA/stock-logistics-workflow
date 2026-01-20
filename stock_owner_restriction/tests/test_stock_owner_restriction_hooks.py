# Copyright 2026 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_owner_restriction import (
    set_default_owner_restriction,
    uninstall_hook,
)


class TestStockOwnerRestrictionHooks(BaseCommon):
    def test_set_default_owner_restriction_hook(self):
        picking_types = self.env["stock.picking.type"].search([], limit=2)
        self.assertEqual(len(picking_types), 2)

        picking_types[0].owner_restriction = False
        picking_types[1].owner_restriction = "unassigned_owner"

        set_default_owner_restriction(self.env)

        self.assertEqual(picking_types[0].owner_restriction, "standard_behavior")
        self.assertEqual(picking_types[1].owner_restriction, "unassigned_owner")

    def test_uninstall_hook_resets_owner_restriction(self):
        picking_types = self.env["stock.picking.type"].search([], limit=2)
        self.assertEqual(len(picking_types), 2)

        picking_types[0].owner_restriction = "picking_partner"
        picking_types[1].owner_restriction = "partner_or_unassigned"

        uninstall_hook(self.env)

        self.assertFalse(picking_types.filtered("owner_restriction"))
