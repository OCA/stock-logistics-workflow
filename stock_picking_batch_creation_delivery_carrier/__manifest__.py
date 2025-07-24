# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch Creation Delivery Carrier",
    "summary": """This module allows to select a delivery carrier
     in criteria for batch creation""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_picking_batch_creation", "stock_delivery"],
    "data": ["wizards/make_picking_batch.xml", "views/stock_picking_batch.xml"],
    "demo": [],
}
