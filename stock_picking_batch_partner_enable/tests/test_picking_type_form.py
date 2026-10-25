# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestPickingTypeForm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Batch fields are behind this group now that batch transfers are
        # part of `stock`.
        cls.env.user.group_ids |= cls.env.ref("stock.group_stock_picking_batch")

    def test_picking_type_form_help_message(self):
        form = Form(self.env["stock.picking.type"])
        # `batch_creation_type` is the field carrying the help on the form
        self.assertIn(
            "Note: Partners must be 'Allowed for batch grouping'",
            form._view["fields"].get("batch_creation_type").get("help"),
            "The help message should contain the note about the partner setting",
        )
