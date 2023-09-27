# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Stock Valuation Fifo Lot",
    "version": "15.0.1.0.0",
    "category": "Warehouse Management",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_account", "stock_no_negative", "stock_landed_costs"],
    "data": [
        "views/stock_valuation_layer_views.xml",
    ],
    "installable": True,
    "maintainers": ["newtratip"],
}
