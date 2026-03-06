# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Lot Auto Remove",
    "summary": """Automatically move remaining quants with a past removal date out "
    "of your stock""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,BCIM,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "product_expiry",
    ],
    "data": [
        "views/stock_picking_type.xml",
        "wizards/stock_lot_removal_wizard.xml",
        "views/stock_warehouse.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "maintainers": ["lmignon"],
    "post_init_hook": "post_init_hook",
}
