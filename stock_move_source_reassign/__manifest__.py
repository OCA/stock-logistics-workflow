# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Source Reassign",
    "summary": """This module allows to reassign a move from a source location
    to another one""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "base_partition",
        "stock",
        "stock_package_level_name",
    ],
    "data": [
        "security/security.xml",
        "views/stock_package_level.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
        "wizards/stock_move_reassign.xml",
    ],
}
