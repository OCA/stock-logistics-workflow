# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Operation Destination Suggestion",
    "summary": """This module allows to show suggestions of
        destination locations from different criteria""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "stock_location_children",
        "stock_location_pending_move",
    ],
    "data": [
        "security/security.xml",
        "wizards/stock_picking_operation_destination_suggestion.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
    ],
}
