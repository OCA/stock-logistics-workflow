# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant remote measure",
    "summary": "Gather the operations weights remotely",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "web_widget_remote_measure",
    ],
    "data": ["wizards/weighing_wizard_views.xml"],
    "assets": {
        "web.assets_backend": [
            "stock_weighing_remote_measure/static/src/**/*.js",
            "stock_weighing_remote_measure/static/src/**/*.scss",
        ],
        "web.assets_qweb": ["stock_weighing_remote_measure/static/src/**/*.xml"],
    },
}
