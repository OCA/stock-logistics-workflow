# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Add product sets in pickings",
    "version": "18.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "product_set"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_product_set_wizard_view.xml",
        "views/stock_picking_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
