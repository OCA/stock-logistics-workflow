# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Picking Unlink Group",
    "summary": "Restrict deletion of pickings to a strict group",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "security/stock_picking.xml",
        "security/ir.model.access.csv",
    ],
}
