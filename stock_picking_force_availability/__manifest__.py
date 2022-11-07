# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Stock Picking Force Availability",
    "summary": "Unreserve some transfers to reserve another one.",
    "version": "14.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking.xml",
        "wizards/stock_picking_force_availability.xml",
    ],
    "installable": True,
}
