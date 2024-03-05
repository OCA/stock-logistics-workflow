# Copyright 2023 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Return Qty Limit",
    "summary": """
        Don't allow to return more items as there were in the original picking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Cetmix,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "maintainers": ["CetmixGitDrone"],
    "data": [
        "wizard/stock_picking_return.xml",
    ],
    "demo": [],
}
