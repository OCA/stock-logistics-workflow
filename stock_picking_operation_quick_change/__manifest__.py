# Copyright 2017-2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Operation Quick Change",
    "summary": "Change location of all picking operations",
    "version": "15.0.1.1.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_picking_wizard_view.xml",
        "views/stock_picking_view.xml",
    ],
}
