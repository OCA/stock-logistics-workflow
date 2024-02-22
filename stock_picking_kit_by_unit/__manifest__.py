# Copyright (C) 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Receive Kit Components by each unit",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Kit reception in order of Kit then Component, including Lot/Serial#",
    "author": "Luz de Airbag, Open Source Integrators, Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["mrp", "purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_picking_kit_wizard_view.xml",
        "views/stock_picking_views.xml",
    ],
    "maintainers": ["dreispt"],
}
