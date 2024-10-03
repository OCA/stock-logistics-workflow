# Copyright 2023 Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Scrap Tier Validation",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "base_tier_validation",
    ],
    "data": [
        "data/mail_message_subtype_data.xml",
        "views/stock_scrap_view.xml",
    ],
}
