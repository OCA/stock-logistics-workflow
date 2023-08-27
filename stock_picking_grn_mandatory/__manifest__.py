# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Type Grn Mandatory",
    "summary": """
        This module allows to require a GRN (Goods Receive Note) when doing a Stock Picking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_grn",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
}
