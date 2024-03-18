# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Auto Create Lot Serial Only",
    "summary": """
        This module restrict lot auto creation to serial only""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_picking_auto_create_lot"],
    "data": ["views/product_template.xml"],
}
