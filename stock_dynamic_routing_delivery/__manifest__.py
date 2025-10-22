# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Dynamic Routing Delivery",
    "summary": "Glue module between stock dynamic routing and delivery",
    "version": "18.0.1.1.0",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich", "jbaudoux"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Warehouse Management",
    "data": ["views/stock_routing.xml"],
    "depends": ["stock_dynamic_routing", "stock_delivery"],
    "auto_install": True,
}
