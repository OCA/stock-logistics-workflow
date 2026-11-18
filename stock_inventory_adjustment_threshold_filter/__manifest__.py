# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Inventory Adjustment Threshold Filter",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "summary": "Filter stock inventory adjustments by cost/quantity threshold "
    "and sign, to select and bulk-apply them",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["lmignon"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "stock_quant_cost_info",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/stock_quant_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_inventory_adjustment_threshold_filter/static/src/**/*",
        ],
    },
    "installable": True,
}
