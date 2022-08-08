# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Scheduler assignation horizon",
    "summary": "Set a timeframe limit to the delivery scheduler",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "external_dependencies": {"python": ["pytz"]},
    "data": [
        "views/res_config_settings_views.xml",
    ],
}
