# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Remote Measure Devices Input on Stock",
    "summary": "Allows to connect to remote devices to record measures in stock fields",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["web_widget_remote_measure", "stock"],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_line_views.xml",
    ],
}
