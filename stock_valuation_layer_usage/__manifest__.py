# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Valuation Layer Usage",
    "version": "13.0.2.0.0",
    "category": "Warehouse Management",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "summary": "Trace where has the stock valuation been used in, including "
    "the quantities taken.",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_account_product_run_fifo_hook"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_valuation_layer_usage_views.xml",
        "views/stock_valuation_layer_views.xml",
        "views/stock_move_views.xml",
    ],
    "installable": True,
}
