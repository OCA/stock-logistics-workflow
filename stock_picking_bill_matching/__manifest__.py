{
    "name": "Stock Picking Bill Matching",
    "version": "16.0.1.0.0",
    "category": "Warehouse",
    "summary": "Match Vendor Bills with Incoming Pickings and their Stock Moves.",
    "description": """
This module allows for direct matching between vendor bill lines and stock moves from incoming pickings.

Features:
- A "Picking Matching" button on Vendor Bills to see and match available receipts.
- A "Bill Matching" button on Incoming Pickings to see and match available vendor bills.
- A dedicated matching interface leveraging the Many2many link from the stock_picking_invoice_link module.
- Ability to create a new Bill from selected stock moves.
- Ability to add bill lines (e.g., freight costs) to an existing picking as new stock moves.
    """,
    "author": "Akretion, Odoo Community Association",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "purchase_stock",
        "stock_picking_invoice_link",
        "purchase_stock_picking_invoice_link",  # Ensures purchase context is available
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/stock_picking_views.xml",
        "views/purchase_order_views.xml",
        "views/picking_bill_line_match_views.xml",
        "wizard/bill_to_picking_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}
