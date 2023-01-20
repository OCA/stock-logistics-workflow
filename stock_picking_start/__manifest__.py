# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Start",
    "summary": """
        Add button to start picking""",
    "version": "16.0.1.0.1",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_picking.xml",
    ],
    "demo": [],
}
