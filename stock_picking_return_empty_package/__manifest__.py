# Copyright 2024 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Empty Package At Picking Return",
    "summary": """Ensure that only package content is put in stock during a picking return""",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
