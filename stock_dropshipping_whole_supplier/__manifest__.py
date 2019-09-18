# Copyright (C) 2019 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
#          David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock DropShipping Whole Supplier",
    "summary": "When sale order with a dropship product, dropship all goods",
    "version": "12.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Warehouse",
    "depends": [
        "stock_dropshipping",
        "sale_management",
    ],
    "data": [
        "views/partner.xml"
    ],
    "demo": [
        "demo/stock.xml"
    ],
    "installable": True,
}
