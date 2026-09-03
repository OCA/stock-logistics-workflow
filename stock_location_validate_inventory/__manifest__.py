# Copyright 2026 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Location Validate Inventory",
    "summary": """Validate the inventory of a location""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "BCIM, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/res_groups.xml",
        "views/stock_location.xml",
    ],
}
