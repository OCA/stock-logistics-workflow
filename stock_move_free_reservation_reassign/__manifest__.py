# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Free Reservation Reassign",
    "summary": """
        Try to reassign a move when its reservation is removed due to the
        related quant becoming unavailable""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": ["views/res_config_settings.xml"],
    "demo": [],
}
