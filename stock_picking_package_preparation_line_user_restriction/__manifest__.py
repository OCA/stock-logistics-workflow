# Copyright 2020 Lorenzo Battistini @ TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Picking Package Preparation Line - Restrict users",
    "summary": "Integration with Package Preparation Line: Restrict some users to "
               "see and use only certain picking types",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "stock_picking_package_preparation_line",
        "stock_picking_type_user_restriction",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
}
