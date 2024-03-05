# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Backorder Reason Grn",
    "summary": """
        This module allows to set on backorder reason if we keep the GRN""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_grn",
        "stock_picking_backorder_reason",
    ],
    "data": ["views/stock_backorder_reason.xml"],
}
