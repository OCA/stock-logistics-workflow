# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Cancel Reason",
    "version": "14.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Stock",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "wizard/stock_picking_cancel_reason_view.xml",
        "views/stock_picking_views.xml",
        "security/ir.model.access.csv",
        "data/stock_picking_cancel_reason.xml",
    ],
    "auto_install": False,
    "installable": True,
}
