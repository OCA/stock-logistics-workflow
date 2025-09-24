# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock landed costs restrict product",
    "summary": """
        This module allows you to associate specific landed costs to products
    """,
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_landed_costs",
    ],
    "data": [
        "views/product_template_views.xml",
        "wizard/res_config_settings_views.xml",
    ],
}
