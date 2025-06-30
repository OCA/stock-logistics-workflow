# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Return Request",
    "version": "15.0.1.0.3",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/stock_return_request_data.xml",
        "views/stock_return_request_views.xml",
        "report/stock_return_report.xml",
        "wizard/suggest_return_request.xml",
    ],
}
