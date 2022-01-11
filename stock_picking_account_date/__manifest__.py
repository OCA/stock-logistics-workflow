# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Customs Account Date",
    "summary": "Define customs date to accounting",
    "version": "15.0.1.0.0",
    "category": "Stock",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "LGPL-3",
    "depends": [
        "stock_account",
        "purchase_stock",
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
}
