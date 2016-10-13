# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Deposit",
    "summary": "Manage deposit locations in your warehouses",
    "version": "9.0.1.0.0",
    "category": "Inventory",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa S.L., "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_view.xml",
        "views/product_view.xml",
        "views/stock_dashboard.xml",
        "data/stock_deposit_data.xml",
        "wizards/stock_quant_wizard_view.xml",
    ],
}
