# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Enable "Packages" feature upon module installation."""
    # Access the environment as the superuser to bypass access rights
    res_config = env["res.config.settings"].create({"group_stock_tracking_lot": True})
    res_config.execute()
