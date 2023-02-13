# Copyright 2022 Tecnativa - César A. Sánchez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock landed costs security",
    "version": "15.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_landed_costs"],
    "data": [
        "security/stock_landed_costs_security.xml",
        "security/ir.model.access.csv",
        "views/stock_landed_costs_view.xml",
    ],
    "installable": True,
    "maintainers": ["cesar-tecnativa"],
}
