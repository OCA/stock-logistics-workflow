# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock landed costs purchase auto",
    "version": "15.0.2.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_landed_costs", "purchase_stock"],
    "data": ["views/purchase_order_view.xml", "views/stock_landed_cost_view.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
