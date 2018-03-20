# -*- coding: utf-8 -*-
# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplierinfo For Customer Picking",
    "version": "10.0.1.0.0",
    "author": "Agile Business Group, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Stock",
    "summary": "This module makes the product customer code visible "
               "in the stock moves of a picking.",
    "license": "AGPL-3",
    "depends": [
        "product",
        "stock",
        "product_supplierinfo_for_customer"
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "installable": True,
}
