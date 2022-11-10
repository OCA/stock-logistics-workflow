# Copyright 2021 Akretion - Florian Mounier
{
    "name": "Stock picking reallocation",
    "summary": """Allow to reallocate moves from a picking to several pickings.""",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_reallocation_views.xml",
        "views/stock_picking_views.xml",
    ],
}
