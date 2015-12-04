# -*- coding: utf-8 -*-
# © <2015> <Sandra Figueroa Varela>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking by Mail",
    "summary": "Send stock picking by email",
    "version": "8.0.1.0.0",
    "author": "<Sandra Figueroa Varela>, Odoo Community Association (OCA)",
    "website": "",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": [
        "base",
        "stock",
        "email_template",
    ],
    "data": [
        'views/stock_picking_mail.xml',
        'views/stock_picking_view.xml',
    ],
    "installable": True
}
