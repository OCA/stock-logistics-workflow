# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock picking batch outgoing",
    "summary": "Allows set on pickings the batch picking from last picking (out)",
    "version": "15.0.1.1.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["sergio-teruel"],
    "category": "Warehouse Management",
    "depends": ["stock_move_propagate_first_move", "stock_picking_batch"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
