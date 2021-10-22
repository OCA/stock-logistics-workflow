# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock picking filter lot",
    "summary": "In picking out lots' selection, filter lots based on their location",
    "version": "13.0.1.0.1",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": ["views/stock_move_line_view.xml", "views/stock_scrap_view.xml"],
}
