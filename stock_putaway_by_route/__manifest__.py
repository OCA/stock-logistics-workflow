# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Putaway By Route",
    "summary": "Add a match by route on putaway, after product and categories",
    "version": "13.0.1.0.1",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "depends": ["stock_putaway_hook"],
    "data": ["views/stock_putaway_rule_views.xml"],
}
