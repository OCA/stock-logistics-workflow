# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Package Reusable",
    "summary": "Select existing reusable package during Put in Pack operation",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/stock_picking_type.xml",
        "views/stock_quant_package.xml",
        # Wizards
        "wizards/select_reusable_package.xml",
    ],
    "post_init_hook": "post_init_hook",
}
