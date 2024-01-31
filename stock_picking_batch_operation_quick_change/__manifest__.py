# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch Operation Quick Change",
    "summary": "Change location of all picking batch operations",
    "version": "15.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_picking_batch"],
    "maintainers": ["sergio-teruel"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_picking_batch_wizard_view.xml",
        "views/stock_picking_batch_view.xml",
    ],
}
