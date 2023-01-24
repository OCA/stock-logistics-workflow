# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Backorder Reason",
    "summary": """
        Allows to add a layer on top of backorder confirmation in order to choose
        a reason. That reason will contain the strategy to apply.""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_picking_type.xml",
        "security/stock_backorder_reason.xml",
        "views/stock_backorder_reason.xml",
        "wizards/stock_backorder_choice.xml",
    ],
    "demo": [
        "demo/stock_backorder_reason.xml",
    ],
}
