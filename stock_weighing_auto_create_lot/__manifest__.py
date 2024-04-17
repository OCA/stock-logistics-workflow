# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Weighing assistant auto create lot",
    "summary": "Allow to create lots from the weighing kanban cards",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_weighing", "stock_picking_auto_create_lot"],
    "data": ["wizards/weighing_wizard_views.xml"],
}
