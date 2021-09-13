# Author: Guewen Baconnier
# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Package Preparation",
    "version": "13.0.1.0.0",
    "author": "Camptocamp, Agile Business Group, Odoo Community Association (OCA)",
    "maintainer": "Camptocamp",
    "license": "AGPL-3",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "security/ir.model.access.csv",
        "security/package_preparation_security.xml",
        "views/stock_picking_package_preparation_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
