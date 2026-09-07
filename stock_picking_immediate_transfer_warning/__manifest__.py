# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Immediate Transfer Warning",
    "summary": """
        Warn before processing a reserved transfer when no
        moves have been explicitly picked.
    """,
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_immediate_transfer_warning_views.xml",
        "views/stock_picking_views.xml",
    ],
}
