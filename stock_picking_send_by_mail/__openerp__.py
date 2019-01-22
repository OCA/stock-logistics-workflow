# -*- coding: utf-8 -*-
# Copyright 2015 - Sandra Figueroa Varela
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking by Mail",
    "summary": "Send stock picking by email",
    "version": "8.0.1.0.0",
    "author": "Sandra Figueroa Varela, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "mail",
    ],
    "data": [
        'data/stock_picking_mail.xml',
        'views/stock_picking_view.xml',
    ],
    "installable": True,
}
