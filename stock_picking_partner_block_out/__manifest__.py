# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Partner Block Out",
    "summary": """
        Adds the possibility to block validation of outgoing picking linked to a partner""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
