# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant in batch pickings",
    "summary": "Launch the weighing assistant from batch pickings",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "stock_picking_batch",
    ],
    "data": ["views/stock_picking_batch_views.xml"],
}
