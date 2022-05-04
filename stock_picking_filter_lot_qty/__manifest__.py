# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock picking filter lot qty",
    "summary": "Stock lot filter only available",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow"
               "12.0/stock_picking_filter_lot_qty",
    "author": "Sergio Corato,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_filter_lot",
    ],
    "data": [
        "views/stock_view.xml",
    ],
}
