# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Operation Destination Suggestion Release Channel",
    "summary": """This module allows to add the release channel to the suggestion
     limitations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_picking_operation_destination_suggestion",
        "stock_release_channel",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}
