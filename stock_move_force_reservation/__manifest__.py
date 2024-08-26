# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Force Reservation",
    "summary": "",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "wizard/stock_move_force_reservation.xml",
    ],
    "installable": True,
}
