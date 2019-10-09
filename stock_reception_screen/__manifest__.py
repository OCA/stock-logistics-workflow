# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Stock - Reception screen",
    "summary": "Dedicated screen to receive/scan goods.",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock",
        "product_expiry",
    ],
    "data": [
        "views/assets.xml",
        "views/stock_move_line.xml",
        "views/stock_picking.xml",
        "views/manual_barcode.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
