# Copyright 2020-2022 ForgeFlow S.L.
#     (<https://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplierinfo Picking",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Stock",
    "summary": "This module makes the product supplier code visible "
    "in the stock moves of a picking.",
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "installable": True,
}
