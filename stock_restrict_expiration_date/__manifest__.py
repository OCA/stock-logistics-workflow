# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Restrict Expiration date",
    "summary": "Add concept of restrict lot on stock move based on specific expiration date",
    "version": "14.0.1.3.1",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock", "product_expiry"],
    "data": [
        "views/stock_picking_views.xml",
    ],
}
