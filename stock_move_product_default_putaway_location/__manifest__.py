# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Move Product Default Putaway Location",
    "summary": """This module allows to help user when transferring moves to get
    the default putaway from move warehouse""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "product_stock_default_putaway",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}
