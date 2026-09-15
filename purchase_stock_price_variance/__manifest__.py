# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Stock Price Variance",
    "summary": "Check purchase price variance at receipt validation",
    "version": "16.0.1.0.0",
    "category": "Stock",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["purchase_stock"],
    "license": "AGPL-3",
    "data": [
        "security/purchase_stock_price_variance_security.xml",
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/res_config_setting_views.xml",
        "views/stock_picking_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
