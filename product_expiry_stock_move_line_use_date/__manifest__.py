# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Product Expiry Stock Move Line Entry",
    "summary": "Enter Best before date on stock move line before lot creation",
    "version": "12.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "product_expiry",
    ],
    "data": [
        "views/stock_move_line.xml",
        "views/stock_picking.xml",
        "views/product.xml",
    ],
    "demo": [
        "demo/product.xml",
    ],
    "installable": True,
}
