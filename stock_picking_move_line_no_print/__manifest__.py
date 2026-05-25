# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "Stock operations hidden in delivery slips",
    "summary": "Hide operations in delivery slips",
    "version": "19.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "chienandalu"],
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/report_delivery.xml",
    ],
}
