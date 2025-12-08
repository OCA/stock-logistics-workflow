# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Stock Dangerous Goods",
    "summary": "Adds utility fields to manage dangerous goods",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
        # OCA/community-data-files
        "l10n_eu_product_adr_dangerous_goods",
    ],
}
