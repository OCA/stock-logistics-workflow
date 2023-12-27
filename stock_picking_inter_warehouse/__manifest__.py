# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Inter Warehouse",
    "version": "14.0.1.2.2",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "PyTech SRL, Ooops404, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_warehouse_views.xml",
    ],
    "demo": [
        "demo/res_config_settings_demo.xml",
        "demo/stock_warehouse_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
}
