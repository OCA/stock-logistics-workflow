# Copyright 2021-22 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Receipt Lot Info",
    "summary": "Be able to introduce more info on lot/serial "
    "number while processing a receipt.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "16.0.1.1.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "LGPL-3",
    "depends": ["stock", "product_expiry"],
    "data": ["views/stock_move_line_views.xml"],
    "installable": True,
}
