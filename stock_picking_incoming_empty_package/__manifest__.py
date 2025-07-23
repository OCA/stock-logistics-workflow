# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


{
    "name": "Stock picking incoming empty package",
    "summary": (
        "Ensure that only package content is put in stock during a picking validation"
    ),
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
