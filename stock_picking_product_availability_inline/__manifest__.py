# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Product Availability Inline",
    "summary": "Show product availability in product drop-down in stock picking form view.",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "base_view_inheritance_extension"],
    "data": ["views/stock_picking_views.xml", "views/stock_move_line_views.xml"],
}
