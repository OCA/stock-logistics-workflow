{
    "name": "Stock Product Restrict",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Restrict product creation based on user permissions",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
        "stock",
    ],
    "data": [
        "security/stock_product_restrict.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
