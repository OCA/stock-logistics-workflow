# -*- coding: utf-8 -*-
# Copyright 2017 Odoo
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scrap",
    "summary": "Adds the ability to scrap products easily.",
    "version": "9.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_scrap_view.xml",
    ],
}
