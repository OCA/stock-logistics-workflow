# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Auto Revert",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "summary": "Returns and recreate the picking",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://forgeflow.com",
    "license": "AGPL-3",
    "depends": ["sale_stock", ],
    "data": ["security/stock_security.xml",
             "view/stock_view.xml",
             ],
    "installable": True,
}
