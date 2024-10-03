# Copyright 2024 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Scrap Tier Validation: MRP compatibility",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "360ERP, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "mrp",
        "stock_scrap_tier_validation",
    ],
    "data": [],
}
