# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestPickingTypeForm(TransactionCase):
    def test_picking_type_form_help_message(self):
        form = Form(self.env["stock.picking.type"])
        self.assertIn(
            "Note: Partners must be 'Allowed for batch grouping'",
            form._view["fields"].get("auto_batch").get("help"),
            "The help message should contain the note about the partner setting",
        )
