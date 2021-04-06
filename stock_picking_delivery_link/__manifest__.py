# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Delivery Link",
    "summary": "Adds link to the delivery on all intermediate operations.",
    "version": "13.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock", "delivery"],
    "data": ["views/stock_picking.xml"],
    "installable": True,
    "license": "AGPL-3",
}
