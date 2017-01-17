# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Backorder to Sale",
    "summary": "Create sale order from backorder an cancel backorder",
    "version": "8.0.1.0.0",
    "category": "Stock",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/stock_view.xml",
    ],
    "installable": True,
}
