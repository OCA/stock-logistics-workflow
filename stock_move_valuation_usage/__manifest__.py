# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Move Valuation Usage",
    "version": "19.0.1.0.0",
    "category": "Warehouse Management",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "summary": "Trace where stock move valuation has been used, including "
    "quantities and values taken.",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["sale", "stock_account_product_run_fifo_hook"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/stock_move_valuation_usage_views.xml",
        "views/stock_move_views.xml",
    ],
    "installable": True,
}
