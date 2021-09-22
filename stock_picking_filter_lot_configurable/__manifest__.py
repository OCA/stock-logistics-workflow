# Copyright 2021 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock picking filter lot",
    "summary": "This module adds a checkbox to configure filtering lots",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_picking_filter_lot", "web_domain_field"],
    "data": [
        "views/stock_move_line_view.xml",
        "views/stock_picking_type_view.xml",
    ],
}
