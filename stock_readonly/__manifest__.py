# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Stock Readonly",
    "summary": "Read-only access to Inventory documents",
    "version": "19.0.1.0.0",
    "category": "Supply Chain/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/stock_menus.xml",
    ],
    "installable": True,
}
