# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Bill Matching",
    "version": "16.0.1.0.0",
    "category": "Warehouse",
    "summary": "Match Vendor Bills with Incoming Pickings and their Stock Moves.",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "purchase_stock",
        "stock_picking_invoice_link",
        "purchase_stock_picking_invoice_link",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/stock_picking_views.xml",
        "views/purchase_order_views.xml",
        "views/picking_bill_line_match_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/bill_to_picking_wizard_views.xml",
    ],
    "demo": ["demo/stock_picking_bill_matching_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}
