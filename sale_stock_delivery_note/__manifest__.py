# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale stock delivery note",
    "description": """Glue module between sale_delivery_note and
    stock_delivery_note to pass this note from sale orders to
    related pickings""",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "stock",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        # OCA/sale-workflow
        "sale_delivery_note",
        # This OCA repo
        "stock_delivery_note",
        # Odoo addons
        "sale_stock",
    ],
    "auto_install": True,
}
