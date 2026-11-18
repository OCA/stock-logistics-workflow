# Copyright 2026 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Fiscal Position",
    "version": "18.0.1.0.0",
    "category": "Generic Modules/Accounting",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
