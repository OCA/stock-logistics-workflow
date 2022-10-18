# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# Copyright 2018-2021 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Expiry Simple",
    "version": "14.0.1.0.0",
    "category": "Product",
    "license": "AGPL-3",
    "summary": "Simpler and better alternative to the official product_expiry module",
    "author": "Akretion,Jarsa Sistemas,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "excludes": ["product_expiry"],
    "data": [
        "data/product_removal.xml",
        "views/stock_production_lot.xml",
        "views/stock_quant.xml",
        "views/stock_move_line.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}
