# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Purchase Order Link",
    "summary": "Link between picking and purchase order",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["purchase_stock"],
    "data": ["views/stock_picking_view.xml"],
    "application": False,
    "installable": True,
}
