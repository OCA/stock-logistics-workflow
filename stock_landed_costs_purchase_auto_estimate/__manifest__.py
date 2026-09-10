# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Landed Costs Purchase Auto Estimate",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_landed_costs_purchase_auto",
        "product_supplierinfo_indirect_cost",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["AaronHForgeFlow"],
}
