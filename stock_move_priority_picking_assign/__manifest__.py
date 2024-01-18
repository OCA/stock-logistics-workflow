# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Priority Picking Assign",
    "summary": """
        This module allows to create a stock movement with a priority and
        transfer it to the picking during assignation (for new ones)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "stock_move_manage_priority",
    ],
    "data": ["views/stock_picking_type.xml"],
}
