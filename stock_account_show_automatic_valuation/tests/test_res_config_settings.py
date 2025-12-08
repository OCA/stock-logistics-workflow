from odoo.tests.common import TransactionCase


class TestResConfigSettingsView(TransactionCase):
    def test_stock_account_valuation_setting_view(self):
        # Fetch the view using its external ID
        view = self.env.ref(
            "stock_account_show_automatic_valuation.res_config_settings_view_form"
        )
        self.assertTrue(view, "View res_config_settings_view_form not found")

        # Parse the view's arch to ensure the custom setting is present
        arch = view.with_context(combined=True).arch_db
        self.assertIn(
            "group_stock_accounting_automatic",
            arch,
            "Field group_stock_accounting_automatic not found in the view",
        )
        self.assertIn(
            "stock_account_show_automatic_valuation",
            arch,
            "Setting ID stock_account_show_automatic_valuation not found in the view",
        )
