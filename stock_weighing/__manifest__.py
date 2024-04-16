# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant",
    "summary": "Weighing assistant for stock operations",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock",
        "web_filter_header_button",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/start_screen_banner.xml",
        "wizards/weigh_operation_selection_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_picking_type_views.xml",
        "wizards/weighing_wizard_views.xml",
    ],
    "demo": [
        "demo/weight_label_demo.xml",
        "demo/picking_type_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_weighing/static/src/**/*.scss",
            "stock_weighing/static/src/**/*.js",
        ],
        "web.assets_qweb": [
            "stock_weighing/static/src/**/*.xml",
        ],
    },
    "post_init_hook": "post_init_hook",
    "pre_init_hook": "pre_init_hook",
}
