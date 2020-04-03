# Copyright 2020 Alan Ramos - Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock picking filter proucts",
    "summary": "Show only available products based on their location",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow"
               "12.0/stock_filter_product",
    "author": "Jarsa, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/stock_scrap_view.xml",
    ]
}
