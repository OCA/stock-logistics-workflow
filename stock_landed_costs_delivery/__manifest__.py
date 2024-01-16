# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock landed costs delivery",
    "version": "15.0.2.0.1",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["delivery_purchase", "stock_landed_costs_purchase_auto"],
    "data": ["views/delivery_carrier_view.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
