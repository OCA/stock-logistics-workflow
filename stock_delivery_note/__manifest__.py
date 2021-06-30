# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Delivery Note",
    "summary": """
        This module allows to fill in a delivery note that will be displayed
        on delivery report""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock", "delivery"],
    "data": ["views/stock_picking.xml", "reports/report_picking.xml"],
}
