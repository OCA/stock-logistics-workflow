# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reception Discrepancy Distribution",
    "summary": "Change demand in stock moves linked to reception one",
    "version": "15.0.1.0.1",
    "development_status": "Beta",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_purchase_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "wizards/stock_reception_discrepancy_distribution_views.xml",
    ],
}
