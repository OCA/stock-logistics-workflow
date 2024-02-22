# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Batch Set Quantity",
    "summary": "Adds buttons to set all reserved quantity in quantity done fields",
    "version": "15.0.1.1.0",
    "development_status": "Beta",
    "category": "Sale",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock_picking_batch",
    ],
    "data": [
        "views/stock_picking_batch_views.xml",
    ],
}
