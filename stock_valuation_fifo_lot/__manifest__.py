# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Stock Valuation Fifo Lot",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Ecosoft, Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_account"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_package_level_views.xml",
        "views/stock_valuation_layer_views.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "maintainers": ["newtratip"],
}
