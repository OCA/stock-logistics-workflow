# Copyright 2024 Tecnativa S.L. - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Force Assign by type",
    "summary": "Force stock allocation based on the picking operation type in Odoo",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
}
