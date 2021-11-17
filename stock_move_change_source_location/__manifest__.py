# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Change Source Location",
    "summary": """
        This module allows you to change the source location of a stock move from the
        picking
    """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_move_change_source_location_wizard.xml",
        "views/stock_picking_view.xml",
    ],
}
