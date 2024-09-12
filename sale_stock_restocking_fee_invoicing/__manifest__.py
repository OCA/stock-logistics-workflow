# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Restocking Fee Invoicing",
    "summary": """
        On demand charge restocking fee for accepting returned goods .""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["sale", "stock", "sale_stock", "stock_account", "stock_picking_kind"],
    "data": [
        "data/product_product.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/stock_move_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/stock_return_picking_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "demo": [],
}
