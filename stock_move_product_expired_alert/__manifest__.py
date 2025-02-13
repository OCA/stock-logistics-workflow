# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Product Expired Entry Alert",
    "summary": """This module allows to alert a set of users of expired products.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["rousseldenis"],
    "depends": [
        "base_partition",
        "mail_activity_team",
        "stock",
        "product_expiry_alert",
    ],
    "data": [
        "views/res_config_settings.xml",
        "data/mail_activity_type.xml",
        "views/stock_picking_type.xml",
    ],
}
