# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Auto Create Lot Quantity",
    "summary": "Auto batch generation by quantity",
    "version": "16.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Ooops, Cetmix OÜ, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_picking_auto_create_lot"],
    "data": [
        "views/product_template_view.xml",
        "views/res_config_settings_view.xml",
    ],
}
